from pydantic import BaseModel, EmailStr, AnyHttpUrl, Field, field_validator # Import BaseModel from pydantic
# Pydantic is a data validation and settings management library for Python
# It allows you to define data models with type annotations and perform validation automatically.
# Pydantic models are used to define the structure of data, validate it, and serialize/deserialize it easily.
from typing import List, Dict, Annotated

class Patient(BaseModel): # Define a Pydantic model for patient information
    """A Pydantic model representing a patient."""
    name: Annotated[str, Field(max_length=100, title="Patient Name", description="The name of the patient")]
    age: int = Field(ge=0, le=120)
    weight: float = Field(ge=0)
    linked_in: AnyHttpUrl
    email: EmailStr
    married: bool
    allergies: List[str]
    contact: Dict[str, str] 
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        """Validate the email format."""
        validated_domains = ['hdfc.com', 'gmail.com', 'yahoo.com']
        domain_name = value.split('@')[-1] # Extract the domain from the email
        if domain_name not in validated_domains:
            raise ValueError(f"Email domain '{domain_name}' is not allowed. Allowed domains: {', '.join(validated_domains)}")
        return value # Return the validated email value
    
patient_info = { 'name': 'Tony', 'age': 26, 'weight': 70.5, 'linked_in': 'https://www.linkedin.com/in/tony', 'email': 'tony@yahoo.com', 'married': False, 'allergies': ['penicillin'], 'contact': {'phone': '123-456-7890'} }

def insert_patient(patient: Patient): # Function to insert a patient into the database
    """Insert a patient into the database."""
    print(patient.name) # Print the patient's name
    print(patient.age) # Print the patient's age
    print('inserted') # Indicate that the patient has been inserted

def update_patient(patient: Patient): # Function to update a patient's information
    """Update a patient's information."""
    print(patient.name) # Print the patient's name
    print(patient.age) # Print the patient's age
    print('updated') # Indicate that the patient has been updated


# Example of using Pydantic to create a model instance from a dictionary
patient1 = Patient(**patient_info) # Unpack the dictionary into the model by using ** operator 

insert_patient(patient1)
update_patient(patient1) # Call the update function with the patient instance
# The Pydantic model automatically validates the data types and structure.
# If the data does not match the model, Pydantic will raise a validation error.