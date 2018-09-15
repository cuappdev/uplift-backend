def is_gym_open(now, gym):
  for (weekday, open_time, close_time) in gym['times']:
    time = now.time()
    if weekday == now.weekday() and time > open_time and time < close_time:
      return True
  return False

