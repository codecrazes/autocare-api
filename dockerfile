FROM python:3.11-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

COPY /autocare /app

RUN pip install -r requirements.txt

RUN rm requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]