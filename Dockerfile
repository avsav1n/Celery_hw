FROM python:3.12-slim AS builder
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN python3 -m venv venv
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/venv /app/venv
COPY . .
ENV PYHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/app/venv/bin:$PATH
EXPOSE 5000
ENTRYPOINT [ "gunicorn",  "server.views:app", "-w", "3", "-b", "0.0.0.0:5000", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-" ]