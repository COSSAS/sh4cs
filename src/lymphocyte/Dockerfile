FROM python:3.10.16-alpine@sha256:4c4097e46608e9b9025a486e3b72d628ac8947a3caa20f142c2e8c0029a12b21 AS base

ENV WORKDIR=/app/lymphocyte
WORKDIR $WORKDIR

ENV PYTHONPATH="$WORKDIR/.." \
    PYTHONUNBUFFERED=1 \
    PATH="$WORKDIR/.venv/bin:$PATH"


FROM base AS installer

RUN apk add --no-cache \
    gcc=14.2.0-r4 \
    python3-dev=3.12.9-r0 \
    musl-dev=1.2.5-r9 \
    linux-headers=6.6-r1

ENV POETRY_VIRTUALENVS_IN_PROJECT="true"
ENV POETRY_CACHE_DIR="/root/.cache"
ENV POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY="true"

RUN pip install --no-cache-dir poetry==1.8.3

COPY poetry.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache  poetry install --without=dev

FROM installer AS dev-installer
RUN --mount=type=cache,target=/root/.cache  poetry install --with=dev

FROM base as dev

COPY --from=dev-installer "$WORKDIR/.venv" "$WORKDIR/.venv"
RUN ln -s "$WORKDIR/test.sh" /test \
    && ln -s "$WORKDIR/coverage.sh" /test-coverage \
    && ln -s "$WORKDIR/lint.sh" /lint
COPY . .
CMD ["flask", "run"]


FROM base AS prod
COPY --from=installer "$WORKDIR/.venv" "$WORKDIR/.venv"
COPY ./ ./

ENV LYMPHOCYTE_LOG_CONFIG=logging.ini

RUN apk add --no-cache \
    libcap=2.71-r0 \
    libcap-setcap=2.71-r0

RUN setcap 'cap_kill=ep' "$(readlink -f "$(which sh)")"
RUN setcap 'cap_kill=ep' "$(readlink -f "$(which python)")"
RUN setcap 'cap_kill=ep' "$(readlink -f "$(which hypercorn)")"

USER 1234:1234

CMD ["hypercorn", "lymphocyte.main:app", "--bind", "0.0.0.0:12345"]
