import os

class Config:
    SECRET_KEY = '6e0be1c8ef5d9ece46efe6531ce56821'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME =  'sms679@cornell.edu'
    MAIL_PASSWORD = 'HarSki2015!!'