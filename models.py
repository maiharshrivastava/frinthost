# models.py
from mongoengine import Document, fields

class Employee(Document):
    """
    MongoDB Document model representing an employee.

    Attributes:
        emp_id (int): Unique employee ID. Must be unique and is required.
        name (str): Employee's name. This field is required.
        age (int): Employee's age. This field is required.
        teams (List[str]): List of teams the employee belongs to. Optional field.
    """
    emp_id = fields.IntField(required=True, unique=True)
    name = fields.StringField(required=True)
    age = fields.IntField(required=True)
    teams = fields.ListField(fields.StringField())

class User(Document):
    """
    MongoDB Document model representing a user.

    Attributes:
        username (str): Unique username for authentication. This field is required.
        password (str): User's hashed password for authentication. This field is required.
    """
    username = fields.StringField(required=True, unique=True)
    password = fields.StringField(required=True)
