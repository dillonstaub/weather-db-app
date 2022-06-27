FROM python:3.10

WORKDIR /weather-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .
COPY data_ingestion.py .
COPY queries.py .
COPY schema.graphql .

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]