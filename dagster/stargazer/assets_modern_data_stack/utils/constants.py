from dagster_postgres.utils import get_conn_string
from dagster._utils import file_relative_path


# AIRBYTE_CONFIG = {"host": "localhost", "port": "8000"}
DBT_PROJECT_DIR = file_relative_path(__file__, "../../transformation_dbt")
DBT_PROFILES_DIR = file_relative_path(__file__, "../../transformation_dbt/config")


DBT_CONFIG = {"project_dir": DBT_PROJECT_DIR, "profiles_dir": DBT_PROFILES_DIR}

PG_DESTINATION_CONFIG = {
    "username": "postgres",
    "password": "password",
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
}

POSTGRES_CONFIG = {
    "con_string": get_conn_string(
        username=PG_DESTINATION_CONFIG["username"],
        password=PG_DESTINATION_CONFIG["password"],
        hostname=PG_DESTINATION_CONFIG["host"],
        port=str(PG_DESTINATION_CONFIG["port"]),
        db_name=PG_DESTINATION_CONFIG["database"],
    )
}
