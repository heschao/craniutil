from python:3

RUN apt-get update && apt-get install -y postgresql

RUN pip install -U \
    nose \
    pycrypto \
    pyyaml \
    sqlalchemy-postgres-copy \
    testing.postgresql

RUN adduser --disabled-password --gecos '' craniuser