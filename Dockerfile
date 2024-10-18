ARG PYTHON_VERSION
ARG NODE_VERSION
ARG ANGULAR_VERSION

FROM python:${PYTHON_VERSION} AS backend-builder
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt .
RUN --mount=type=secret,id=pip_index_url \
  --mount=type=secret,id=pip_trusted_host \
  --mount=type=secret,id=pip_proxy \
  export PIP_INDEX_URL=$(cat /run/secrets/pip_index_url) && \
  export PIP_TRUSTED_HOST=$(cat /run/secrets/pip_trusted_host) && \
  export PIP_PROXY=$(cat /run/secrets/pip_proxy) && \
  python3 -m venv /opt/venv && \
  pip3 install --no-cache-dir -r ./requirements.txt

FROM node:${NODE_VERSION}-slim AS frontend-builder
WORKDIR /app
COPY ./package*.json .
RUN --mount=type=secret,id=http_proxy \
  --mount=type=secret,id=https_proxy \
  export HTTP_PROXY=$(cat /run/secrets/http_proxy) && \
  export HTTPS_PROXY=$(cat /run/secrets/https_proxy) && \
  npm install && \
  npm install -g @angular/cli@${ANGULAR_VERSION}
COPY . .
RUN ng build

FROM python:${PYTHON_VERSION}-slim as app
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
RUN --mount=type=secret,id=http_proxy \
  --mount=type=secret,id=https_proxy \
  export http_proxy=$(cat /run/secrets/http_proxy) && \
  export https_proxy=$(cat /run/secrets/https_proxy) && \
  apt-get update && \
  apt-get install -y --no-install-recommends libgomp1 && \
  rm -rf /var/lib/apt/lists/*
COPY --from=backend-builder /opt/venv /opt/venv
COPY --from=frontend-builder /app/dist/frontend/browser /app/frontend
COPY ./src/video_insights_processor /app/video_insights_processor
ENTRYPOINT ["python3", "-m", "video_insights_processor"]
