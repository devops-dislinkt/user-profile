FROM python:3.10-slim-buster
WORKDIR /home/service/
RUN pip install poetry
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install
WORKDIR /home/service/user_profile_service
ENTRYPOINT ["poetry", "run", "python", "run.py"]