FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev g++ libffi-dev

COPY ./requirements.txt /app/requirements.txt

COPY ./model.pkl /app/model.pkl

COPY ./vehicle-problems.csv /app/vehicle-problems.csv

COPY /autocare /app

RUN pip install -r requirements.txt

RUN rm requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
