# Deployment of the backend

## Using Postgres Locally
By default the repo is set to use SQLite. We want to be able to develop with Postgres, as Postgres is used in production. 
The `local-postgres` directory contains a `docker-compose.yml` file that runs Postgres. It also has configuraton file - `local-postgres.cfg` . To use it, just copy this file to `/instance/override.cfg`, and the backend will use Postgres instead of SQLite.

Don't forget to start Postgres by running:
```
cd deployment/local-postgres
docker-compose up
```

## Running a Dockerized Backend
The backend is deployed in a Docker container. We want to make sure it works by running it locally. The docker folder contains a `docker-compose.yml` file that sets up a Postgres database and a backend container, and configures them to work together.

Note that you will need to apply migrations to the database and ingest the manuscripts before you can really work with
the backend. The `init-docker-env.py` script does this for you, just run it.
