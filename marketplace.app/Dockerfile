FROM python:3.6
COPY ./requirements.txt /app/
RUN pip install -r app/requirements.txt
COPY marketplace/ /app/marketplace/
COPY ./runserver.py /app
COPY ./manage.py /app
WORKDIR /app
ENV FLASK_APP=runserver.py
