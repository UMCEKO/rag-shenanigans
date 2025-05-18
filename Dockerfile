FROM python:3.12.3

WORKDIR /backend

ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY . .


CMD ["python", "main.py"]
