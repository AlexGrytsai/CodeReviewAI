FROM python:3.12.0-alpine
LABEL authors="agrytsai"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache g++ unixodbc-dev curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

RUN adduser \
    --disabled-password \
    --home /app \
    st_user

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

RUN chown -R st_user:st_user /app

USER st_user

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
