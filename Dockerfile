FROM python:3.10-alpine

WORKDIR /usr/src/app

COPY code/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY code/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
