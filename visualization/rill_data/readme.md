# Rill Data

[Rill Data](https://www.rilldata.com/) one of the latest BI tools and based on DuckDB. It's fully interactive and using DuckDB as a caching layer.

Unfortunately the data cannot be read live from airbyte postgres, but you can copy the data with a simple comand as CSV and read these with Rill. The commands below show you how you could create a snapshot and vizualize these data.


when you followed the tutorial on airbyte.com you have a postgres the airbyte postgres db exposted on `5435` and you can export tables to CSV with: 

Install DuckDB cmd line with: [Docs Installation](https://duckdb.org/docs/installation/).


Run DuckDB with:
```sh
duckdb
```
and export data as CSV:
```sh
INSTALL postgres_scanner;
LOAD postgres_scanner;
COPY(SELECT * FROM postgres_scan('host=127.0.0.1 user=docker dbname=airbyte port=5435 password=docker', 'public', 'jobs')) TO 'jobs.csv' (FORMAT CSV);
```
Note: make sure you have the latest [postgres_scanner](https://github.com/duckdblabs/postgres_scanner) version, otherwise you might get `IO Error: Unsupported Postgres type jsonb`.


As soon as views are supported, we can export our created mart-views with dbt (does not work as of now):
```sh
COPY(SELECT * FROM postgres_scan('host=127.0.0.1 user=docker dbname=airbyte port=5435 password=docker', 'monitoring_core', 'core_airbyte_sync_status')) TO 'core_airbyte_sync_status.csv' (FORMAT CSV);
```

Next you can install, load data into rill and start it with:
```sh 
rill import-source jobs.csv
rill start
```
and open at [localhost:8080](http://localhost:8080/).

Note: If you just want to have a quick glance at rill, I added a small export `jobs.csv`, which you could import and test.
