# Deployment of the backend

## Using Postgres Locally
By default the repo is set to use SQLite. We want to be able to develop with Postgres, as Postgres is used in production. 
The `local-postgres` directory contains a `docker-compose.yml` file that runs Postgres. It also has configuraton file - `local-postgres.cfg` . To use it, just copy this file to `/instance/override.cfg`, and the backend will use Postgres instead of SQLite.

Don't forget to start Postgres by running:
```
cd deployment/local-postgres
docker-compose up
```
