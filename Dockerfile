FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev python3-dev
COPY requirements.txt requirements.txt
RUN pip3 install requests
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]
