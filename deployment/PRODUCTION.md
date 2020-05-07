# Deploying the backend to our production environment

## Difference components
### Database
The production environment consists of a Postgres instance managed by ElephantSQL, and an Azure Web Application running
a Docker container of the backend.

The user and password are available elsewhere.

### Docker
The docker image of the backend is stored as chelem/plague-backend .

Pushing to master updates the :latest image. Pushing a tag vX.Y.Z creates a new image with the tag X.Y.Z.

### Azure Web App
The Azure Web app is called plague-transcriptions, in the Research Software Company's Azure account. The web app is reachable from https://plague-backend.researchsoftwarehosting.org

## Deploying an Update

### Source
After you finish testing the new version, change the version in `app_config.py` and push to master and create a new git tag. This will trigger the build process of the docker image.

### Database
You may need to run migrations on the database. For this, set the environment variable for SQL_ALCHEMY as follows:

    $env:SQLALCHEMY_DATABASE_URI="postgres://rfsuagfn:<password>@drona.db.elephantsql.com:5432/rfsuagfn"

(this is for Powershell, use your favorite's shell syntax. The password is obviously stored elsewhere)

Then run

    flask db upgrade

### Azure Web App
Log in to the Azure Portal, go to the plague-transcriptions web application, choose Container Settings and set the "image and optional tag" field to the new version tag.

Then switch to "Overview" and restart the application.

Access https://plague-backend.researchsoftwarehosting.org/info to see that the new version has been installed.