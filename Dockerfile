FROM python:3.12-alpine

RUN apk add --no-cache gcc musl-dev libffi-dev nodejs npm bash curl libc6-compat git build-base linux-headers


RUN curl -sSL https://sdk.cloud.google.com | bash /dev/stdin --disable-prompts --install-dir=/usr/local
ENV PATH="$PATH:/usr/local/google-cloud-sdk/bin"
ENV CLOUDSDK_PYTHON=python3


RUN npm install -g firebase-tools


COPY functions/requirements.txt /app/functions/requirements.txt


RUN pip install --break-system-packages -r /app/functions/requirements.txt


COPY . /app/
