# Airbyte monitoring

## setup virtual env, dependencies and dbt profile (attention: if one exists, it will be renamed as `~/.dbt/profiles_backup.yml`:
```sh
poetry install
poetry shell 
task setup_dbt
task setup_dbt_profile1
task setup_dbt_profile2
task run 
````

or run dbt manually with:
```sh
dbt run 
````
*or `task run`*



