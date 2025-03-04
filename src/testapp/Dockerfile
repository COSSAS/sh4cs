FROM python:3.10.16-alpine@sha256:4c4097e46608e9b9025a486e3b72d628ac8947a3caa20f142c2e8c0029a12b21

WORKDIR /opt/app

ENV PYTHONPATH=/opt/app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG BUILD_VERSION=dev
ENV BUILD_VERSION=${BUILD_VERSION}

USER 1000:1000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
