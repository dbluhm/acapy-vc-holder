FROM python:3.10-slim-bookworm as base
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y curl && apt-get clean
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python -

FROM python:3.10-slim-bookworm
WORKDIR /usr/src/app
COPY --from=base /opt/poetry /opt/poetry
ENV PATH="/opt/poetry/bin:$PATH"

RUN poetry config virtualenvs.in-project true

# Setup project
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only demo

COPY ./demo/demo.py ./

ENTRYPOINT ["poetry", "run", "python", "-m", "demo"]
