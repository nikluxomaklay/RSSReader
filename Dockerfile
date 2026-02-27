FROM python:3.14-slim

ENV UV_VERSION=0.10.0
ENV PATH="/app/.venv/bin:${PATH}"

RUN apt-get update && \
    apt-get -y install gcc && \
    apt-get -y install libpq-dev && \
    pip install "uv==$UV_VERSION"

WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv sync --frozen --no-cache --no-dev

COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh

COPY --exclude=.env ./src .

ENTRYPOINT ["/app/entrypoint.sh"]