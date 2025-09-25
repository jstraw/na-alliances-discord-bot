FROM python:3-trixie
RUN apt update && apt install python3-poetry
VOLUME /alliancebot
WORKDIR /alliancebot
ENTRYPOINT exec poetry install && poetry run python3 na_alliances_discord_bot/__init__.py