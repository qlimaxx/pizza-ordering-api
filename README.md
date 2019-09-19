## Development and testing environments

  - Docker Compose (1.24.1, build 4667896b)
  - Docker  (1.13.1, build 092cba3)
  - Python docker image (python:3.7-alpine)
  - PostgreSQL docker image (postgres:11-alpine)


## How to run

Make sure that docker-compose and docker are installed on your system. Clone the repository and then change directory to the cloned repository.

Run the API

```sh
docker-compose up -d api
```

Run the database migrations and load data into the database

```sh
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py loaddata pizzas.json
```

## API documentation

You can find the API documentation in `docs/api.md`.

## How to run tests

Run the tests

```sh
docker-compose up test
```
