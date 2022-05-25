FROM python:3.8.10-slim-buster
WORKDIR /home/service/
RUN pip install poetry
COPY ./poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install
ENTRYPOINT ["poetry", "run", "flask", "run", "--host", "0.0.0.0"]