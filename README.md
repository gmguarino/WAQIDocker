# WAQI Docker

This environment runs two docker containers to produce an applet that retrieves the air quality index in the current location, using the World Air Quality Index (WAQI) API.

## The Containers
The `docker-compose.yml` script launches two containers:
1. The first container is a `python:3.7-alpine` container that runs a flask app to comunicate with the WAQI server.
2. The second container runs a PostgreSQL image (`postgres:latest`) to store retrieved data.

## Setup
To setup the WAQI API you need to first register on [Air Quality Open Data Platform] and retieve an API token. Secondly, edit line 18 in the app.py script to add you API token.
```
API_TOKEN = "INSERT YOUR API TOKEN HERE"
```
You are now good to go!

[Air Quality Open Data Platform]:https://aqicn.org/data-platform/token/#/

## Running
Clone the repository locally and from the main folder run: </br>
```
docker-compose up -d
```
(`-d` runs in detached mode ie. background)</br></br>
The app will be visible on `localhost:5000`.</br>
To stop the containers, run:
```
docker-compose down
```
## The App
As previously said the app will be visible on  `localhost:5000`, and will load the current air quality on access.

A recent history can also be viewed at  `localhost:5000/history/`. As a default this will show only the last entry in the database. To specify the number of entries to be visualised use
```
localhost:5000/history/?limit=<limit>
```
Where `<limit>` is to be substituted by the number to required entries.