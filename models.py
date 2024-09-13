# models.py
from mongoengine import Document, fields

class Employee(Document):
    emp_id = fields.IntField(required=True, unique=True)
    name = fields.StringField(required=True)
    age = fields.IntField(required=True)
    teams = fields.ListField(fields.StringField())

class User(Document):
    username = StringField()
    password = StringField()