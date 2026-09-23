from datetime import datetime, timezone

from sqlalchemy import func

from src.models.facility import Facility
from src.models.workout import Workout


def _ensure_utc(value):
    """Normalize a datetime to UTC, or return None if value is None.

    Naive datetimes are treated as UTC. Aware values are converted to UTC.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _challenge_window(challenge):
    """Return the challenge start and end as timezone-aware UTC datetimes."""
    return _ensure_utc(challenge.start_date), _ensure_utc(challenge.end_date)


def _extract_target(challenge, default=1):
    """Read ``target`` from ``challenge.rule_config`` as a positive integer.

    Falls back to ``default`` when missing or not coercible to int. Minimum
    returned value is 1.
    """
    rule_config = challenge.rule_config or {}
    target = rule_config.get("target", default)
    try:
        target = int(target)
    except (TypeError, ValueError):
        target = default
    return max(target, 1)


def _extract_event_type(event):
    """Return a string event type from a dict-like event payload, or None."""
    if not event:
        return None
    return (
        event.get("rule_type")
        or event.get("event_type")
        or event.get("type")
        or event.get("name")
    )


def _extract_event_timestamp(event):
    """Parse an event's time field to a UTC datetime, or None if unavailable.

    Checks common keys (``timestamp``, ``occurred_at``, ``created_at``, etc.).
    Accepts ``datetime`` instances or ISO 8601 strings (including trailing ``Z``).
    """
    if not event:
        return None

    raw_timestamp = (
        event.get("timestamp")
        or event.get("occurred_at")
        or event.get("created_at")
        or event.get("completed_at")
        or event.get("shared_at")
        or event.get("opened_at")
    )

    if raw_timestamp is None:
        return None

    if isinstance(raw_timestamp, datetime):
        return _ensure_utc(raw_timestamp)

    if isinstance(raw_timestamp, str):
        normalized = raw_timestamp.replace("Z", "+00:00")
        try:
            return _ensure_utc(datetime.fromisoformat(normalized))
        except ValueError:
            return None

    return None


def _is_in_window(timestamp, start_date, end_date):
    """True if ``timestamp`` is between ``start_date`` and ``end_date`` (inclusive)."""
    if timestamp is None:
        return False
    return start_date <= timestamp <= end_date


def _event_matches(event, expected_types):
    """True if the event's type matches any string in ``expected_types`` (case-insensitive)."""
    event_type = _extract_event_type(event)
    if not event_type:
        return False

    normalized_event_type = str(event_type).upper()
    normalized_expected_types = {expected_type.upper() for expected_type in expected_types}
    return normalized_event_type in normalized_expected_types


def _build_metadata(rule_type, current_count, target, source, extra=None):
    """Assemble the standard evaluator metadata dict, optionally merged with ``extra``."""
    metadata = {
        "rule_type": rule_type,
        "current_count": current_count,
        "target": target,
        "source": source,
    }
    if extra:
        metadata.update(extra)
    return metadata


def evaluate_checkin_count(user, challenge, db_session, event=None):
    """Complete when the user has at least ``target`` workouts in the challenge window.

    Counts rows in ``Workout`` for ``user`` where ``workout_time`` falls between
    the challenge's normalized start and end. ``event`` is ignored.

    Returns:
        Tuple of ``(satisfied, metadata)`` where ``satisfied`` is whether the
        count meets the target, and ``metadata`` includes counts, window, and
        ``source="database"``.
    """
    start_date, end_date = _challenge_window(challenge)
    target = _extract_target(challenge)

    current_count = (
        db_session.query(func.count(Workout.id))
        .filter(
            Workout.user_id == user.id,
            Workout.workout_time >= start_date,
            Workout.workout_time <= end_date,
        )
        .scalar()
        or 0
    )

    metadata = _build_metadata(
        "CHECKIN_COUNT",
        current_count=current_count,
        target=target,
        source="database",
        extra={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    return current_count >= target, metadata


def evaluate_distinct_gyms(user, challenge, db_session, event=None):
    """Complete when the user works out at at least ``target`` distinct gyms in the window.

    Counts distinct ``Facility.gym_id`` for the user's workouts joined to
    ``Facility``. ``event`` is ignored.

    Returns:
        ``(satisfied, metadata)`` with ``source="database"``.
    """
    start_date, end_date = _challenge_window(challenge)
    target = _extract_target(challenge)

    current_count = (
        db_session.query(func.count(func.distinct(Facility.gym_id)))
        .select_from(Workout)
        .join(Facility, Facility.id == Workout.facility_id)
        .filter(
            Workout.user_id == user.id,
            Workout.workout_time >= start_date,
            Workout.workout_time <= end_date,
        )
        .scalar()
        or 0
    )

    metadata = _build_metadata(
        "DISTINCT_GYMS",
        current_count=current_count,
        target=target,
        source="database",
        extra={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    return current_count >= target, metadata


def evaluate_app_open_days(user, challenge, db_session, event=None):
    """Event-only rule: one qualifying app-open in-window yields count 1, else 0.

    Matches event types ``APP_OPEN_DAYS``, ``APP_OPEN``, or ``APP_OPENED``
    (case-insensitive). ``db_session`` is unused.

    Returns:
        ``(satisfied, metadata)`` with ``source="event_only"`` and match details.
    """
    start_date, end_date = _challenge_window(challenge)
    target = _extract_target(challenge)
    event_timestamp = _extract_event_timestamp(event)
    matched_event = _event_matches(event, {"APP_OPEN_DAYS", "APP_OPEN", "APP_OPENED"})
    current_count = 1 if matched_event and _is_in_window(event_timestamp, start_date, end_date) else 0

    metadata = _build_metadata(
        "APP_OPEN_DAYS",
        current_count=current_count,
        target=target,
        source="event_only",
        extra={
            "matched_event": matched_event,
            "event_timestamp": event_timestamp.isoformat() if event_timestamp else None,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    )
    return current_count >= target, metadata


def evaluate_invite_completion(user, challenge, db_session, event=None):
    """Event-only rule: invitee completion attributed to the inviter.

    Count is 1 when the event type matches invite-completion aliases, the
    event's ``inviter_id`` or ``user_id`` equals ``user.id``, and the event
    timestamp is in the challenge window. ``db_session`` is unused.

    Returns:
        ``(satisfied, metadata)`` with ``source="event_only"``.
    """
    start_date, end_date = _challenge_window(challenge)
    target = _extract_target(challenge)
    event_timestamp = _extract_event_timestamp(event)
    matched_event = _event_matches(
        event,
        {"INVITE_COMPLETION", "INVITE_COMPLETED", "INVITE_ONBOARDING_COMPLETED"},
    )

    inviter_id = None if not event else event.get("inviter_id", event.get("user_id"))
    current_count = (
        1
        if matched_event and inviter_id == user.id and _is_in_window(event_timestamp, start_date, end_date)
        else 0
    )

    metadata = _build_metadata(
        "INVITE_COMPLETION",
        current_count=current_count,
        target=target,
        source="event_only",
        extra={
            "matched_event": matched_event,
            "event_timestamp": event_timestamp.isoformat() if event_timestamp else None,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    )
    return current_count >= target, metadata


def evaluate_share_workout(user, challenge, db_session, event=None):
    """Event-only rule: user shared a workout during the challenge window.

    Count is 1 when the event matches share aliases, ``event["user_id"]`` is
    the subject user, and the timestamp is in-window. Default ``target`` is 1.
    ``db_session`` is unused.

    Returns:
        ``(satisfied, metadata)`` with ``source="event_only"``.
    """
    start_date, end_date = _challenge_window(challenge)
    target = _extract_target(challenge, default=1)
    event_timestamp = _extract_event_timestamp(event)
    matched_event = _event_matches(event, {"SHARE_WORKOUT", "WORKOUT_SHARED", "SHARE_WORKOUT_SUMMARY"})

    event_user_id = None if not event else event.get("user_id")
    current_count = (
        1
        if matched_event and event_user_id == user.id and _is_in_window(event_timestamp, start_date, end_date)
        else 0
    )

    metadata = _build_metadata(
        "SHARE_WORKOUT",
        current_count=current_count,
        target=target,
        source="event_only",
        extra={
            "matched_event": matched_event,
            "event_timestamp": event_timestamp.isoformat() if event_timestamp else None,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    )
    return current_count >= target, metadata
