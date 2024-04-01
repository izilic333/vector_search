FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends wget lsb-release gnupg2 && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 libgdal-dev gettext postgresql-client-16 vim git openssh-client libpq-dev libgnutls28-dev libcurl3-gnutls gcc g++ librdkafka-dev && \
    apt-get clean && \
    mkdir /app && \
    useradd -m app && \
    chown app:app /app && \
    mkdir -p /home/app/.vscode-server/extensions /home/app/.vscode-server-insiders/extensions && \
    chown -R app /home/app/.vscode-server /home/app/.vscode-server-insiders && \
    python3 -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python3 -

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
COPY start_app.sh /app/
USER app

ENV VIRTUAL_ENV=/home/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m venv --copies ~/venv && \
    poetry --no-interaction --no-ansi -v install --with dev,test,docs

# Download the model
RUN python -c "from transformers import BertTokenizer; BertTokenizer.from_pretrained('bert-base-multilingual-uncased')"

# Download Word2Vec model

COPY --chown=app:app . /app/
RUN chmod +x /app/start_app.sh && \
    chown app:app /app/start_app.sh && \
    git config --global --add safe.directory /app && \
    python -m nltk.downloader punkt

EXPOSE 8000
