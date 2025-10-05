from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal,Optional
from fastapi.responses import JSONResponse
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the Patient", examples=["P001", "P002"])]
    name: Annotated[str, Field(..., description="Name of the Patient", examples=["Ayan", "Mateen"])]
    city: Annotated[str, Field(..., description="Name of the city", examples=["Karachi", "Lahore"])]
    age: Annotated[int, Field(..., gt=0, lt=100, description="Age of the Patient")]
    gender: Annotated[Literal["Male", "Female", "Others"], Field(..., description="Gender of the Patient")]
    height: Annotated[float, Field(..., description="Height of the Patient (meters)")]
    weight: Annotated[float, Field(..., description="Weight of the Patient (kg)")]

    @computed_field
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None,gt=0)]
    gender: Annotated[Optional[Literal["Male", "Female", "Others"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None,gt=0)]
    weight: Annotated[Optional[float], Field(default=None,gt=0)]

def load_data():
    try:
        with open("patient.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_data(data):
    with open("patient.json", "w") as f:
        json.dump(data, f)

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    data[patient.id] = patient.model_dump(exclude=["id"])
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})
@app.put("/edit/{patient_id}")
def update_patient(patient_id:str,patient_update:PatientUpdate):
    data =load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not Found")
    existing_patient_info=data[patient_id]
    updated_patient_info=patient_update.model_dump(exclude_unset=True)
    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value
    existing_patient_info["id"]=patient_id
    patient_pydantic_object=Patient(**existing_patient_info)
    patient_pydantic_object.model_dump(exclude="id")
    data[patient_id]=existing_patient_info
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})
@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=400,detail="Patient not found")
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200,content={"message":"Patient deleted"})
