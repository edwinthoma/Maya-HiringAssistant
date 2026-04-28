# Dockerfile
# Instructions for building the Maya hiring assistant container.
# Cloud Build reads this file and produces a container image.

# FROM — specifies the base image we start from.
# Think of it like a clean computer with Python 3.12 already installed.
# slim-bookworm is a lightweight version — smaller image size, faster deployment.
FROM python:3.12-slim-bookworm

# WORKDIR — sets the working directory inside the container.
# All subsequent commands run from this folder.
# If it doesn't exist, Docker creates it automatically.
WORKDIR /app

# COPY requirements.txt first — before copying the rest of the code.
# Why? Docker caches each step. If requirements.txt hasn't changed,
# Docker skips the pip install step on future builds — much faster rebuilds.
COPY requirements.txt .

# RUN — executes a command during the build process.
# --no-cache-dir prevents pip from storing downloaded packages,
# keeping the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# COPY — copies everything else from your project folder into the container.
# The first . means "everything in the current local directory"
# The second . means "into the current WORKDIR inside the container"
COPY . .

# EXPOSE — documents that the app listens on port 8080.
# Cloud Run expects your app to listen on port 8080 specifically.
EXPOSE 8080

# ENV — sets environment variables inside the container.
# Streamlit needs these to run correctly in a containerized environment.
# server.port=8080 — Cloud Run routes traffic to port 8080
# server.address=0.0.0.0 — accepts connections from outside the container
# server.headless=true — runs without trying to open a browser
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# CMD — the command that runs when the container starts.
# This is what actually launches your Streamlit app.
CMD ["streamlit", "run", "app.py"]