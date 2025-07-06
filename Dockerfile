FROM python:3.9-slim

WORKDIR /app

COPY repo_automator.py .
COPY generator.py .
COPY entrypoint.sh .

RUN pip install --no-cache-dir watchdog packaging

RUN chmod +x /app/entrypoint.sh

RUN useradd -m -u 1000 pi && \
    chown -R pi:pi /app

USER pi

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["sh", "-c", "python repo_automator.py & python -m http.server 8008 --directory /app/web"]