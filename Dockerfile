FROM python:3.10.0 as python-base

ARG APP_NAME=internal
ARG APP_PATH=/opt/$APP_NAME
ARG PYTHON_VERSION=3.10.0
ARG POETRY_VERSION=1.1.13

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR $APP_PATH
COPY ./poetry.lock ./pyproject.toml ./
COPY ./$APP_NAME ./$APP_NAME

WORKDIR $APP_PATH
RUN poetry install --no-dev

ENTRYPOINT ["poetry", "run"]
