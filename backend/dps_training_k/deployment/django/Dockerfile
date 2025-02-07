ARG PYTHON_VERSION=3.12-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} AS python

# Python 'run' stage
FROM python AS python-run-stage

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev gcc python3-dev musl-dev \
  # Translations dependencies
  gettext \
  # OCaml and MonPoly dependencies
  git opam \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Initialize OPAM and switch to the required OCaml version
RUN opam init -y --disable-sandboxing && \
    opam switch create 4.11.1 && \
    eval $(opam env) && \
    opam install dune -y

# Clone the MonPoly repository
RUN git clone https://bitbucket.org/monpoly/monpoly.git /home/opam/monpoly

# Set the working directory
WORKDIR /home/opam/monpoly

# Install dependencies
RUN eval $(opam env) && opam install --deps-only -y .

# Build and install MonPoly
RUN eval $(opam env) && dune build --release && dune install
ENV PATH="/root/.opam/4.11.1/bin:${PATH}"
# Verify MonPoly installation and PATH
RUN eval $(opam env) &&which monpoly && echo $PATH

WORKDIR ${APP_HOME}
# Install requirements
RUN pip install -r requirements.txt

COPY ./deployment/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./deployment/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./deployment/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

ENTRYPOINT ["/entrypoint"]
