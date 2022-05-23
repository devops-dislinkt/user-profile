FROM python:3.8.10
WORKDIR /code
RUN pip install poetry
COPY ./poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . /code/
ENTRYPOINT ["poetry", "run", "flask", "run", "--host", "0.0.0.0"]