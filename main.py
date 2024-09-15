from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from mongoengine import connect, Document, fields
from typing import List, Optional
from pydantic import BaseModel, Field
import logging
import traceback
from passlib.context import CryptContext

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to MongoDB
connect(db="hrms", host="localhost", port=27017)

class Employee(Document):
    """
    MongoDB Document model representing an employee.

    Attributes:
        emp_id (int): Unique employee ID.
        name (str): Employee's name.
        age (int): Employee's age.
        teams (List[str]): List of teams the employee belongs to.
    """
    emp_id = fields.IntField(required=True, unique=True)
    name = fields.StringField(required=True)
    age = fields.IntField(required=True)
    teams = fields.ListField(fields.StringField())

class EmployeeResponse(BaseModel):
    """
    Pydantic model for the response format of employee data.

    Attributes:
        emp_id (int): Employee ID.
        name (str): Employee's name.
        age (int): Employee's age.
        teams (List[str]): List of teams the employee belongs to.
    """
    emp_id: int
    name: str
    age: int
    teams: List[str]

class EmployeeCreate(BaseModel):
    """
    Pydantic model for creating a new employee.

    Attributes:
        emp_id (int): Employee ID, must be greater than 1.
        name (str): Employee's name.
        age (int): Employee's age.
        teams (List[str]): List of teams the employee belongs to.
    """
    emp_id: int = Field(..., gt=1, description="Employee ID must be greater than 1")
    name: str
    age: int
    teams: List[str]

@app.get("/")
def home():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A message indicating the welcome to the HRMS API.
    """
    return {"message": "Welcome to the HRMS API"}

@app.get("/get_employee/{emp_id}", response_model=EmployeeResponse)
def get_employee(emp_id: int):
    """
    Endpoint to retrieve employee details by ID.

    Args:
        emp_id (int): The employee ID to retrieve.

    Returns:
        EmployeeResponse: Details of the employee.

    Raises:
        HTTPException: 400 if emp_id is not greater than 1.
        HTTPException: 404 if employee is not found.
        HTTPException: 500 for internal server errors.
    """
    if emp_id <= 1:
        raise HTTPException(status_code=400, detail="Employee ID must be greater than 1")
    
    try:
        emp = Employee.objects.get(emp_id=emp_id)
        return EmployeeResponse(
            emp_id=emp.emp_id,
            name=emp.name,
            age=emp.age,
            teams=emp.teams
        )
    except Employee.DoesNotExist:
        raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        logger.error(f"Error fetching employee with emp_id {emp_id}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/create_employee/", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate):
    """
    Endpoint to create a new employee record.

    Args:
        employee (EmployeeCreate): The employee data to create.

    Returns:
        EmployeeResponse: Details of the created employee.

    Raises:
        HTTPException: 500 for internal server errors.
    """
    try:
        emp = Employee(emp_id=employee.emp_id, name=employee.name, age=employee.age, teams=employee.teams)
        emp.save()
        return EmployeeResponse(
            emp_id=emp.emp_id,
            name=emp.name,
            age=emp.age,
            teams=emp.teams
        )
    except Exception as e:
        logger.error(f"Error creating employee: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/search_employees", response_model=List[EmployeeResponse])
def search_employees(name: Optional[str] = None, age: Optional[int] = None):
    """
    Endpoint to search for employees based on optional name and age parameters.

    Args:
        name (Optional[str]): Name to filter employees by.
        age (Optional[int]): Age to filter employees by.

    Returns:
        List[EmployeeResponse]: List of employees matching the search criteria.

    Raises:
        HTTPException: 500 for internal server errors.
    """
    query = {}
    if name:
        query["name"] = name
    if age is not None:
        query["age"] = age
    
    logger.info(f"Executing query: {query}")

    try:
        employees = Employee.objects(**query)
        logger.info(f"Found employees: {employees}")
        response = [
            EmployeeResponse(
                emp_id=emp.emp_id,
                name=emp.name,
                age=emp.age,
                teams=emp.teams
            )
            for emp in employees
        ]
        logger.info(f"Response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error searching employees: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

class NewEmployee(BaseModel):
    """
    Pydantic model for adding a new employee.

    Attributes:
        emp_id (int): Employee ID.
        name (str): Employee's name.
        age (int): Employee's age.
        teams (List[str]): List of teams the employee belongs to.
    """
    emp_id: int
    name: str
    age: int
    teams: List[str]

@app.post("/add_employee")
def add_employee(employee: NewEmployee):
    """
    Endpoint to add a new employee record.

    Args:
        employee (NewEmployee): The employee data to add.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: 500 for internal server errors.
    """
    try:
        new_employee = Employee(emp_id=employee.emp_id, name=employee.name, age=employee.age, teams=employee.teams)
        new_employee.save()
        return {"message": "Employee added successfully"}
    except Exception as e:
        logger.error(f"Error adding employee: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

class User(Document):
    """
    MongoDB Document model representing a user.

    Attributes:
        username (str): Unique username for authentication.
        hashed_password (str): Hashed password for authentication.
    """
    username = fields.StringField(required=True, unique=True)
    hashed_password = fields.StringField(required=True)

class NewUser(BaseModel):
    """
    Pydantic model for user registration.

    Attributes:
        username (str): Username for registration.
        password (str): Password for registration.
    """
    username: str
    password: str

@app.post("/sign_up")
def sign_up(new_user: NewUser):
    """
    Endpoint to register a new user with hashed password.

    Args:
        new_user (NewUser): The user data to register.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: 500 for internal server errors.
    """
    try:
        hashed_password = pwd_context.hash(new_user.password)
        user = User(username=new_user.username, hashed_password=hashed_password)
        user.save()
        return {"message": "New user created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to authenticate a user.

    Args:
        form_data (OAuth2PasswordRequestForm): The login credentials.

    Returns:
        dict: Success message if credentials are valid.

    Raises:
        HTTPException: 401 for invalid credentials.
        HTTPException: 404 for user not found.
        HTTPException: 500 for internal server errors.
    """
    try:
        user = User.objects.get(username=form_data.username)
        if not pwd_context.verify(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"message": "Login successful"}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error logging in user {form_data.username}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/secure-endpoint")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    """
    Secured endpoint requiring a valid token.

    Args:
        token (str): Token for accessing the secured endpoint.

    Returns:
        dict: Message indicating access to a secured endpoint.

    Notes:
        In a real application, token validation would be performed here.
    """
    # Token validation logic would be implemented here.
    return {"message": "You have access to this secure endpoint"}
