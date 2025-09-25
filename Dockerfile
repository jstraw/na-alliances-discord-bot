FROM python:3-trixie
RUN apt update && apt install -y python3-poetry
ENV POETRY_VIRTUALENVS_PATH=/venvs
WORKDIR /venvs
VOLUME /alliancebot
WORKDIR /alliancebot
RUN --mount=type=bind,target=/alliancebot,src=. POETRY_VIRTUALENVS_PATH=/venvs poetry install
ENTRYPOINT ["poetry", "run", "python3", "na_alliances_discord_bot/__init__.py"]