FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

#CMD ["flask", "run", "--host=0.0.0.0", "--port=6543"]
CMD ["python", "main.py"]