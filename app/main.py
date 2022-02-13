from http.client import HTTPException
from app.models.student import StudentModel, UpdateStudentModel
from fastapi import FastAPI, Body, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.db import db


app = FastAPI()


@app.get("/")
async def root_node():
    return {"Message":"Hello World"}

@app.get("/students/")
async def all_students():
    students = await db["students"].find().to_list(1000)
    return students

@app.post("/students/", response_description="Add new student", response_model=StudentModel)
async def create_student(student: StudentModel = Body(...)):
    student = jsonable_encoder(student)
    new_student = await db["students"].insert_one(student)
    created_student = await db["students"].find_one({"_id": new_student.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)

@app.get("/students/{id}/", response_description="Get a single student", response_model=StudentModel)
async def show_student(id: str):
    student = await db["students"].find_one({"_id":id})
    if student:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@app.delete("/students/{id}/", response_description="Delete a single student", response_model=StudentModel)
async def delete_student(id: str):
    delete_result = await db["students"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@app.put("/students/{id}/", response_description="Update a single student", response_model=StudentModel)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    student = {k: v for k, v in student.dict().items() if v is not None}

    print("STUDENT : {}".format(student))

    if len(student) >= 1:
        update_result = await db["students"].update_one({"_id": id}, {"$set": student})

        if update_result.modified_count == 1:
            updated_student = await db["students"].find_one({"_id": id})
            if updated_student is not None:
                return updated_student
    existing_student = await db["students"].find_one({"_id": id})
    if existing_student is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")