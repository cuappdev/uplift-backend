from . import *

def get_all_routines():
  return Routine.query.all()

def get_routine_by_id(routine_id):
  return Routine.query.filter(Routine.id == routine_id).first()

def get_routines_by_category(category):
  return Routine.query.filter(Routine.category == category).all()

def get_routines_by_title(title):
  return Routine.query.filter(Routine.title == title).all()

def get_routines_by_post_id(post_id):
  return Routine.query.filter(Routine.post_id == post_id).all()

def serialize_routine(routine):
  return routine_schema.dump(routine).data

def create_routine(category, post_id, steps, title):
  new_routine = Routine(
    category=category, 
    post_id=post_id,
    steps=steps, 
    title=title)
  db_utils.commit_model(new_routine)
  return True, new_routine