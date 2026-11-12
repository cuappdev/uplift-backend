"""Request-scoped, uncached batches for weekly progress GraphQL fields."""
from promise import Promise
from promise.dataloader import DataLoader
from sqlalchemy import func

from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.models.user_workout_week import UserWorkoutWeek
from src.utils.workout_streaks import WORKOUT_TIMEZONE, active_days, as_utc, week_midnight, week_start


class WorkoutProgressLoader(DataLoader):
    """Batch weekly rows and effective goals without retaining resolved values."""

    def __init__(self, session):
        """Bind this request's database session and disable result caching."""
        # Mutation fields execute serially; do not reuse values from an earlier
        # mutation's response when a later mutation changes the same user.
        super().__init__(cache=False)
        self.session = session

    def batch_load_fn(self, keys):
        """Return active-day counts and goals in the requested key order."""
        results = {}
        for monday in {key[1] for key in keys}:
            user_ids = {key[0] for key in keys if key[1] == monday}
            rows = (
                # Scalar columns also bypass stale ORM identity-map values.
                self.session.query(
                    UserWorkoutWeek.user_id, UserWorkoutWeek.checked_in_days, UserWorkoutWeek.workout_goal
                )
                .filter(UserWorkoutWeek.user_id.in_(user_ids), UserWorkoutWeek.week_start == monday)
                .all()
            )
            for row in rows:
                results[(row.user_id, monday)] = (active_days(row.checked_in_days), row.workout_goal)
            missing = user_ids - {row.user_id for row in rows}
            if missing:
                # Return only the latest effective goal per dormant user. A
                # window avoids fetching their entire goal history into Python.
                history = (
                    self.session.query(
                        UserWorkoutGoalHistory.user_id,
                        UserWorkoutGoalHistory.workout_goal,
                        func.row_number()
                        .over(
                            partition_by=UserWorkoutGoalHistory.user_id,
                            order_by=(UserWorkoutGoalHistory.effective_at.desc(), UserWorkoutGoalHistory.id.desc()),
                        )
                        .label("position"),
                    )
                    .filter(
                        UserWorkoutGoalHistory.user_id.in_(missing),
                        UserWorkoutGoalHistory.effective_at <= week_midnight(monday),
                    )
                    .subquery()
                )
                for user_id, goal in self.session.query(history.c.user_id, history.c.workout_goal).filter(
                    history.c.position == 1
                ):
                    results[(user_id, monday)] = (0, goal if goal is not None and 1 <= goal <= 7 else 1)
        return Promise.resolve(
            [
                results.get((user_id, monday), (0, goal if goal and 1 <= goal <= 7 else 1))
                for user_id, monday, goal in keys
            ]
        )


def load_workout_progress(info, session, user, now):
    """Share a loader within Flask's request or an explicit GraphQL context."""
    context = getattr(info, "context", None)
    attribute = "_workout_progress_loader"
    if context is None:
        loader = WorkoutProgressLoader(session)
    elif isinstance(context, dict):
        loader = context.get(attribute)
        if loader is None:
            loader = context[attribute] = WorkoutProgressLoader(session)
    else:
        loader = getattr(context, attribute, None)
        if loader is None:
            loader = WorkoutProgressLoader(session)
            setattr(context, attribute, loader)
    monday = week_start(as_utc(now).astimezone(WORKOUT_TIMEZONE).date())
    key = (user.id, monday, user.workout_goal)
    if context is None:
        # Preserve direct resolver calls used outside GraphQL execution.
        return loader.batch_load_fn([key]).get()[0]
    return loader.load(key)
