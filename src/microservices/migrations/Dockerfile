FROM ui-ux-base:latest

WORKDIR /app

USER root
COPY src/microservices/migrations/ .

RUN chown -R fastapi-user:fastapi-user /app

USER fastapi-user

CMD ["alembic", "upgrade", "head"]