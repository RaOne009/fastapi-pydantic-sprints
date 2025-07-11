from fastapi import FastAPI, Path, HTTPException, Query 
from pydantic import BaseModel, Field, computed_field
from fastapi.responses import JSONResponse
from typing import Annotated, Literal, Optional
import json

app = FastAPI() # Initialize FastAPI application
# Load patient data from a JSON file
# This file should contain a dictionary with patient IDs as keys and patient details as values.
class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open("patients.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file)

@app.get("/") # Define the root endpoint
def hello_world():
    return {"message": "Patient management system API"}

@app.get("/about")
def about():
    return {"message": "This is a simple FastAPI application."}

@app.get("/patients")
def get_patients():
    data = load_data()
    return data

@app.get("/patients/{patient_id}") # Define an endpoint to retrieve a specific patient by ID
def get_patient(patient_id: str = Path(..., description= "The ID of the patient to retrieve", example = "P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort') # Define an endpoint to sort patients based on height, weight, or BMI
def sort_patients(sort_by: str = Query(..., description='sort on the basis of height, weight, bmi'), order: str = Query('asc', description='sort order: asc or desc')): # Define query parameters for sorting
    data = load_data()
    if sort_by not in ['height', 'weight', 'bmi']:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid sort order")
    # Convert data to a list of tuples for sorting
    sorted_order = True if order == 'asc' else False # Determine the sorting order based on the query parameter
    sorted_data = sorted(data.values(), key= lambda x: x.get(sort_by, 0), reverse = sorted_order) # Sort the patient data
    return sorted_data

@app.post('/create_patient') # Define an endpoint to create a new patient

def create_patient(patient: Patient):
    # Load existing data
    data = load_data()

    # Check if patient already exists 
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    # new patient added to the data
    data[patient.id] = patient.model_dump(exclude=['id'])  # Convert Pydantic model to dict

    # Save the updated data back to the JSON file
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})

@app.put('/edit/{patient_id}')

def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}') # Define an endpoint to delete a patient by ID

def delete_patient(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={'message': 'Patient deleted successfully'})

