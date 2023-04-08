
from database import Base 
from sqlalchemy import Column

class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String(100), nullable=False)
    description = Column(String{100}, nullable=False)
    gym_id = Column(Integer, ForeignKey('gym.id'), nullable=False)
    location = Column(String{100}, nullable=False)
    image_url = Column(String(1000), nullable=True)
    preparation = Column(String(1000), nullable=True)
    instructor = Column(String(100), nullable=False)
    is_cancelled = Column(Boolean, nullable=True, default_value=False)
    # category = Column() for the categories of classes - like Yoga classes, HIIT classes ... 

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.gym_id = kwargs.get("gym_id")
        self.location = kwargs.get("location")
        self.image_url = kwargs.get("image_url")
        self.preparation = kwargs.get("preparation")
        self.instructor = kwargs.get("instructor")
        self.is_cancelled = kwargs.get("is_cancelled")

    def simple_serialize(self):
        return {}

    def serialize(self):
        # THERE IS A PYTHONIC WAY TO DO THIS IN ONE LINE but im on a plane and too tired to think of efficient ways to do this
        preparation = "" 
        if self.preparation:
            preparation = self.preparation 
        
        return {
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "gym_id":self.gym_id,
            "location":self.location, 
            "image_url":self.image_url,
            "preparation": preparation,
            "instructor": self.instructor, 
            "is_cancelled": self.is_cancelled
        }


class ClassTime(Base):
    __tablename__ = 'classtime'

    id = Column(Integer, primary_key=True)
    daytime_id = Column(Integer, ForeignKey('daytime.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.id'), nullable=False)

    def __init__(self, **kwargs):
        self.daytime_id = kwargs.get("daytime_id")
        self.class_id = kwargs.get("class_id")

    def serialize(self):
        return {
            "daytime_id": self.daytime_id,
            "class_id": self.class_id
        }

    
