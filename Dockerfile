FROM python:3.11-slim-bullseye

WORKDIR /app

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.1.14

ENV PATH="$PATH:$POETRY_HOME/bin"

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y postgresql-client libpq-dev

# Install Poetry
RUN pip install --upgrade pip && pip install poetry 

# Copy poetry.lock and pyproject.toml
COPY poetry.lock pyproject.toml ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the code files
COPY src/ .

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]