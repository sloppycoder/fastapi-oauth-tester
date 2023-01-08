FROM python:3.10-bullseye as builder
LABEL org.opencontainers.image.source https://github.com/sloppycoder/fastapi-oauth-tester.git
LABEL org.opencontainers.image.description "Test API for testing with OAuth providers"

run apt-get update && apt-get install -y \
    build-essential 

COPY requirements.txt .
RUN pip install --root="/install" -r requirements.txt

# runtime
FROM python:3.10-slim-bullseye
LABEL org.opencontainers.image.source https://github.com/sloppycoder/biznext_event_tool

COPY --from=builder /install /
COPY . .

CMD [ "python", "app.py", "--host=0.0.0.0", "--port=5000"]
EXPOSE 5000