FROM python:3.12-slim

RUN pip install poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /metrics_consumer
COPY  metrics_consumer/pyproject.toml  metrics_consumer/poetry.lock ./
RUN poetry lock && poetry install --no-root && rm -rf $POETRY_CACHE_DIR

#COPY metrics_consumer/src/Kafka ./Kafka
COPY metrics_consumer/src/NATS ./NATS
COPY storage/graph_base ./graph_base
COPY storage/timescaledb ./timescaledb
COPY metrics_consumer/src/consume.py .
COPY metrics_consumer/src/settings.py .

#RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "-m", "consume"]