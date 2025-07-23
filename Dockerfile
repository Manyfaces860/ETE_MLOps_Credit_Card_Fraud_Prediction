FROM python:3.11-slim-buster

COPY --from=ghcr.io/astral-sh/uv:0.7.9 /uv /uvx /bin/

WORKDIR /app

ADD ./pyproject.toml ./pyproject.toml
ADD ./uv.lock ./uv.lock

RUN uv sync --locked

ADD . .

EXPOSE 8000