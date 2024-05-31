FROM python:3.10-slim-bookworm as base
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y curl && apt-get clean
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
COPY pyproject.toml poetry.lock README.md ./
RUN mkdir acapy_vc_holder && touch acapy_vc_holder/__init__.py
RUN poetry install --with acapy

COPY ./acapy_vc_holder ./acapy_vc_holder
ENTRYPOINT ["poetry", "run", "aca-py"]
