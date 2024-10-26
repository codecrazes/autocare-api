import sys
from http import HTTPStatus
from typing import Annotated

import joblib
import numpy as np
import pandas as pd
from conf.settings import Settings
from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Diagnosis, User, Vehicle, VehicleProblem
from schemas import DiagnosisCreate, DiagnosisSchema
from security import get_current_user
from sklearn.preprocessing import LabelEncoder
from sqlalchemy.orm import Session

sys.path.append("..")
settings = Settings()

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

model = joblib.load("model.pkl")


def predict_and_generate_report(symptoms_input, vehicle_model):
    data = pd.read_csv("vehicle-problems.csv")

    symptoms = data["Sintomas"].str.get_dummies(";")
    le = LabelEncoder()
    data["Modelo Codificado"] = le.fit_transform(data["Modelos Comuns"])

    input_data = symptoms.columns.isin(symptoms_input)
    input_data = input_data.astype(int)

    model_code = le.transform([vehicle_model])[0] if vehicle_model in le.classes_ else -1

    input_combined = np.append(input_data, model_code).reshape(1, -1)

    predicted_problem = model.predict(input_combined)[0]

    problem_details = data[data["Problema"] == predicted_problem].iloc[0]

    response = {
        "predicted_problem": predicted_problem,
        "problem_details": problem_details,
    }

    return response


# @router.post("/", status_code=HTTPStatus.CREATED, response_model=DiagnosisSchema)
# def diagnosis(problem_id: int, session: Session, user: CurrentUser):
#     problem = session.get(VehicleProblem, problem_id)
#     vehicle = session.get(Vehicle, problem.vehicle_id)

#     if not vehicle:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

#     if not problem:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Problem not found")

#     if user.id != vehicle.user_id:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

#     session_response = requests.post(
#         f"{settings.WATSON_BASE_URL}/v2/assistants/{settings.WATSON_CLIENT_ID}/sessions?version=2021-11-27",
#         auth=HTTPBasicAuth("apikey", settings.WATSON_API_KEY),
#     )

#     session_id = session_response.json()["session_id"]

#     response = requests.post(
#         f"{settings.WATSON_BASE_URL}/instances/{settings.WATSON_INSTANCE_ID}/v2/assistants/{settings.WATSON_CLIENT_ID}/sessions/{session_id}/message?version=2021-11-27",
#         auth=HTTPBasicAuth("apikey", settings.WATSON_API_KEY),
#         headers={"Content-Type": "application/json"},
#         json={"input": {"text": problem.description}},
#     )

#     response_json = response.json()

#     symptoms = []

#     for symptom in response_json["output"]["entities"]:
#         symptoms.append(symptom["value"])

#     prediction = predict_and_generate_report(symptoms, vehicle.model)

#     db_diagnosis = Diagnosis(
#         vehicle_problem_id=problem.id,
#         user_id=user.id,
#         symptoms=str(symptoms),
#         predicted_problem=prediction["predicted_problem"],
#         description=prediction["problem_details"]["Descrição do Problema"],
#         service=prediction["problem_details"]["Serviço Recomendado"],
#         price=prediction["problem_details"]["Preço Médio do Reparo"],
#         price_details=prediction["problem_details"]["Peças e Valores"],
#     )

#     session.add(db_diagnosis)
#     session.commit()
#     session.refresh(db_diagnosis)

#     diagnosis_response = {
#         "id": db_diagnosis.id,
#         "vehicle_problem_id": db_diagnosis.vehicle_problem_id,
#         "symptoms": db_diagnosis.symptoms,
#         "predicted_problem": db_diagnosis.predicted_problem,
#         "problem_details": {
#             "description": db_diagnosis.description,
#             "service": db_diagnosis.service,
#             "price": db_diagnosis.price,
#             "price_details": db_diagnosis.price_details,
#         },
#     }

#     return diagnosis_response


@router.post("/v2/", status_code=HTTPStatus.CREATED, response_model=DiagnosisSchema)
def diagnosis_v2(diagnosisCreate: DiagnosisCreate, session: Session, user: CurrentUser):
    vehicle = session.get(Vehicle, diagnosisCreate.vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

    if user.id != vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    prediction = predict_and_generate_report(diagnosisCreate.symptoms, vehicle.model)

    db_diagnosis = Diagnosis(
        vehicle_problem_id=diagnosisCreate.vehicle_problem_id,
        user_id=user.id,
        symptoms=str(diagnosisCreate.symptoms),
        predicted_problem=prediction["predicted_problem"],
        description=prediction["problem_details"]["Descrição do Problema"],
        service=prediction["problem_details"]["Serviço Recomendado"],
        price=prediction["problem_details"]["Preço Médio do Reparo"],
        price_details=prediction["problem_details"]["Peças e Valores"],
    )

    session.add(db_diagnosis)
    session.commit()
    session.refresh(db_diagnosis)

    diagnosis_response = {
        "id": db_diagnosis.id,
        "vehicle_problem_id": db_diagnosis.vehicle_problem_id,
        "symptoms": db_diagnosis.symptoms,
        "predicted_problem": db_diagnosis.predicted_problem,
        "problem_details": {
            "description": db_diagnosis.description,
            "service": db_diagnosis.service,
            "price": db_diagnosis.price,
            "price_details": db_diagnosis.price_details,
        },
    }

    return diagnosis_response


@router.get("/user", response_model=list[DiagnosisSchema])
def get_diagnosis_by_user(session: Session, user: CurrentUser):
    db_diagnosis = session.query(Diagnosis).filter(Diagnosis.user_id == user.id).all()

    if not db_diagnosis:
        return []

    diagnosis_response = []

    for diagnosis in db_diagnosis:
        diagnosis_response.append(
            {
                "id": diagnosis.id,
                "vehicle_problem_id": diagnosis.vehicle_problem_id,
                "symptoms": diagnosis.symptoms,
                "predicted_problem": diagnosis.predicted_problem,
                "problem_details": {
                    "description": diagnosis.description,
                    "service": diagnosis.service,
                    "price": diagnosis.price,
                    "price_details": diagnosis.price_details,
                },
            }
        )

    return diagnosis_response


@router.get("/", response_model=DiagnosisSchema)
def get_diagnosis(diagnosis_id: int, session: Session, user: CurrentUser):
    diagnosis = session.get(Diagnosis, diagnosis_id)

    if not diagnosis:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Diagnosis not found")

    problem = session.get(VehicleProblem, diagnosis.vehicle_problem_id)

    vehicle = session.get(Vehicle, problem.vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

    if user.id != vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    diagnosis_response = {
        "id": diagnosis.id,
        "vehicle_problem_id": diagnosis.vehicle_problem_id,
        "symptoms": diagnosis.symptoms,
        "predicted_problem": diagnosis.predicted_problem,
        "problem_details": {
            "description": diagnosis.description,
            "service": diagnosis.service,
            "price": diagnosis.price,
            "price_details": diagnosis.price_details,
        },
    }

    return diagnosis_response
