FROM python:3.10-slim

WORKDIR /app

RUN \
    printf '#!/bin/sh\n\n' > /entrypoint.sh \
    && printf 'echo "[*] installing dependencies"\n' >> /entrypoint.sh \
    && printf 'poetry install --no-interaction --sync\n\n' >> /entrypoint.sh \
    && printf 'echo "[*] executing script \"${1}\""\n' >> /entrypoint.sh \
    && printf 'exec poetry run "${1}"\n' >> /entrypoint.sh \
    && chmod 0755 /entrypoint.sh \
    && python -m pip install --no-color --no-cache-dir --no-python-version-warning --disable-pip-version-check poetry==1.2.1

ENTRYPOINT [ "/entrypoint.sh" ]