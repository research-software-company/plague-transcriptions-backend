# plague-transcriptions-backend
The backend of the Plague Transcription Project

## Setting up the Backend
To set up the backend, you need to have Python 3.7 or later installed. Then do the following, from the root folder of this project.

### Create the virtual environment
`py -m venv env --prompt "plague-backend"`

Activate the virtual environment:
`source env/bin/activate` on OS X and Linux, or `env\scripts\activate` on Windows.

Install requirements
`pip install -r requirements.txt`

You will need to activate the virtual environment every time you want to access the backend

### Initialize the database
You can initialize an SQLite database with everyhting you need for development. Activate the virtual environment if you haven't already done so and run

```
flask db upgrade
flask ingest data-files/manuscripts.xlsx
flask ingest data-files/manuscripts.xlsx --sheet 3
```

You now have a database you can use.

To start over with the database, just delete the `plague-transcriptions.db` file and start over.

### Running the backend
To run it on port 5000 just run

`flask run`

# Deployment
All information regarding deployment is in the `deployment` folder.

