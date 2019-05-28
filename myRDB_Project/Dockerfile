# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.7

USER root
WORKDIR /myRDB_Project

RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get install -y \
    && pip install --upgrade pip \
    && pip install psycopg2 \
    && pip install uwsgi

# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /myRDB_Project/requirements.txt
RUN pip install -r requirements.txt

# Now copy in our code, and run it
COPY . /myRDB_Project
EXPOSE 8000
CMD ["uwsgi", "--ini", ":8000", "/myRDB_Project/uwsgi.ini"]
