# pull official base image
FROM python:3.10

# set work directory
WORKDIR /book_over_there

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install psycopg2-binary and other dependencies
RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && pip install psycopg2-binary


# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]