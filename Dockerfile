FROM python:3.7

EXPOSE 8000

RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip

ADD ./project /code
WORKDIR /code

RUN pip install -r /code/requirements.txt

CMD python manage.py runserver 0.0.0.0:8000
