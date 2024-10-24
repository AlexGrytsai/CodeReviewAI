FROM python:3.12.0-alpine
LABEL authors="agrytsai"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache g++ unixodbc-dev curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    st_user

USER st_user
