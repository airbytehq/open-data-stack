
# Dagster Orchestration Layer

## Getting started
setup virtual env, dependencies and dbt profile (attention: if one exists, it will be renamed as `~/.dbt/profiles_backup.yml`:
```sh
poetry install
poetry shell 
````

To startup the dagster UI run:
```sh
dagit
````

If you try to kick off a run immediately, it will fail, as there is no source data to ingest/transform, nor is there an active Airbyte connection. To get everything set up properly, read on.

## Set up local Postgres

We'll use a local postgres instance as the destination for our data. You can imagine the "destination" as a data warehouse (something like Snowflake).

To get a postgres instance with the required source and destination databases running on your machine, you can run:

```
docker pull postgres
docker run --name local-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres
```

## Set up Airbyte

Now, you'll want to get Airbyte running locally. The full instructions can be found [here](https://docs.airbyte.com/deploying-airbyte/local-deployment), but if you just want to run some commands (in a separate terminal):

```
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Once you've done this, you should be able to go to http://localhost:8000, and see Airbyte's UI.

## Set up data and connections




