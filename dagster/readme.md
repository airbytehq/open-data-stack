
# Dagster Orchestration Layer

## Getting started
setup virtual env, dependencies:
```bash
cd stargazer
pip install -e ".[dev]"
```

If you try to kick off a run immediately, it will fail, as there is no source data to ingest/transform, nor is there an active Airbyte connection. To get everything set up properly, read on.

## Set up local Postgres

We'll use a local postgres instance as the destination for our data. You can imagine the "destination" as a data warehouse (something like Snowflake).

To get a postgres instance with the required source and destination databases running on your machine, you can run:

```bash
docker pull postgres
docker run --name local-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres
```

## Set up Airbyte

Now, you'll want to get Airbyte running locally. The full instructions can be found [here](https://docs.airbyte.com/deploying-airbyte/local-deployment), but if you just want to run some commands (in a separate terminal):

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Once you've done this, you should be able to go to http://localhost:8000, and see Airbyte's UI.

## Set up data and connections

```bash
dagster-me check --module assets_modern_data_stack.assets.stargazer:airbyte_reconciler
```

```bash
dagster-me apply --module assets_modern_data_stack.assets.stargazer:airbyte_reconciler
```
➡️ Make sure you set the environment variable `AIRBYTE_PASSWORD` on your laptop. The default password is `password`. As well as  [create](https://github.com/settings/tokens) a token  `AIRBYTE_PERSONAL_GITHUB_TOKEN` for fetching the stargazers from the public repositories.

## Start the UI of Dagster called Dagit

To startup the dagster UI run:
```bash
dagit
````

You'll see the assets of airbyte, dbt that are created automatically in this demo.

You can click "materialize" inside dagit to sync airbyte connections and run dbt.


## Start the BI Dashbaord with Meltano

Start it in a seperate shell and follow the docs [Metabase Readme](../../visualization/metabase/readme.md).


See a step by step guide on [Airbyte Blog](https://airbyte.com/blog/).




