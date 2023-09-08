FROM python:3.11.4-slim-bullseye as python

WORKDIR /app


COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /app
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
