FROM python:3.10-slim-buster
WORKDIR /home/service/

ENV HTTP_PROXY=http://proxy.uns.ac.rs:8080
ENV http_proxy=http://proxy.uns.ac.rs:8080
ENV HTTPS_PROXY=http://proxy.uns.ac.rs:8080
ENV https-proxy=http://proxy.uns.ac.rs:8080

RUN pip install --proxy=http://proxy.uns.ac.rs:8080 poetry

#RUN pip install poetry
COPY ./poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry lock && poetry install
ENTRYPOINT ["poetry", "run", "python", "run.py"]
