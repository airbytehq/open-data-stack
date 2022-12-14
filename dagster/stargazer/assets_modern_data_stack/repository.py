from dagster_airbyte import airbyte_resource
from dagster_dbt import dbt_cli_resource

from dagster import (
    repository,
    with_resources,
)

# from . import assets
from .db_io_manager import db_io_manager
from .utils.constants import DBT_CONFIG, POSTGRES_CONFIG
from .assets.stargazer import airbyte_assets, dbt_assets  # , metabase_dashboard


@repository
def assets_modern_data_stack():
    return [
        airbyte_assets,
        with_resources(
            dbt_assets,  # load_assets_from_package_module(assets),
            resource_defs={
                "dbt": dbt_cli_resource.configured(DBT_CONFIG),
                "db_io_manager": db_io_manager.configured(POSTGRES_CONFIG),
            },
        ),
        # metabase_dashboard,
    ]
