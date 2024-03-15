# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

CMD exec uvicorn --workers 4 --host 0.0.0.0 --port $PORT app.main:app 