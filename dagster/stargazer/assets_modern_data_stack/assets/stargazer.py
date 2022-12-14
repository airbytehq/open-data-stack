from dagster import asset
from dagster_airbyte import (
    AirbyteManagedElementReconciler,
    airbyte_resource,
    AirbyteConnection,
    AirbyteSyncMode,
    load_assets_from_connections,
)
from dagster_airbyte.managed.generated.sources import GithubSource
from dagster_airbyte.managed.generated.destinations import LocalJsonDestination, PostgresDestination
from typing import List
from dagster_dbt import load_assets_from_dbt_project


from bs4 import BeautifulSoup
import os
import requests

import asyncio
import aiohttp
from ..utils.constants import DBT_PROJECT_DIR


TOKEN = os.environ.get("AIRBYTE_PERSONAL_GITHUB_TOKEN", "please-set-your-token")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "please-set-your-token")


airbyte_instance = airbyte_resource.configured(
    {
        "host": "localhost",
        "port": "8000",
        "username": "airbyte",
        "password": {"env": "AIRBYTE_PASSWORD"},
        "request_timeout": 60,
    }
)
# two other possibilities to initialize the airbyte instance
# airbyte_assets = load_assets_from_airbyte_project(
#     project_dir="../../../../airbyte/test",
# )

# airbyte_assets = with_resources(
#     [load_assets_from_airbyte_project(project_dir="path/to/airbyte/project")],
#     {"airbyte": airbyte_instance},
# )


async def get(url, session):
    try:
        # check if status_code is 200
        async with session.get(url) as response:
            if response.status == 200:
                return url
            else:
                return None

    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def check_websites_exists(urls) -> List[str]:
    async with aiohttp.ClientSession() as session:
        # get url and sessionm if return is not None
        tasks = [get(url, session) for url in urls]
        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]
    return results
    # print("Finalized all. Return is a list of len {} outputs.".format(len(results)))


def get_awesome_repo_list() -> str:

    url = "https://github.com/igorbarinov/awesome-data-engineering"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    # parse all links into a list starting with github.com
    links = [link.get("href") for link in soup.find_all("a") if link.get("href").startswith("https://github.com")]
    # remove links that start with url
    links = [link for link in links if not link.startswith(url) and not link.endswith("github.com")]
    # remove last slash if there
    links = [link[:-1] if link.endswith("/") else link for link in links]
    # remove repos without organization
    links = [link for link in links if len(link.split("/")) == 5]
    # check if links are still existing in parallel to save time
    existings_links = asyncio.run(check_websites_exists(links))
    # remove `https://github.com/` from links
    links = [link.replace("https://github.com/", "") for link in existings_links]
    # return links as a string with blank space as separator
    return " ".join(links)


gh_awesome_de_list_source = GithubSource(
    name="gh_awesome_de_list",
    credentials=GithubSource.PATCredentials(TOKEN),
    start_date="2020-01-01T00:00:00Z",
    # repository=get_awesome_repo_list(),  # "prometheus/haproxy_exporter",
    repository="prometheus/haproxy_exporter",
    page_size_for_large_streams=100,
)

postgres_destination = PostgresDestination(
    name="postgres",
    host="localhost",
    port=5432,
    database="postgres",
    schema="public",
    username="postgres",
    password=POSTGRES_PASSWORD,
    ssl_mode=PostgresDestination.Disable(),
)


local_json_destination = LocalJsonDestination(
    name="local-json",
    destination_path="/local/cereals_out.json",
)

stargazer_connection = AirbyteConnection(
    name="fetch_stargazer",
    source=gh_awesome_de_list_source,
    destination=postgres_destination,
    stream_config={"stargazers": AirbyteSyncMode.incremental_append_dedup()},
    normalize_data=True,
)
airbyte_reconciler = AirbyteManagedElementReconciler(
    airbyte=airbyte_instance,
    connections=[stargazer_connection],
)


# load airbyte connection from above pythonic definitions
airbyte_assets = load_assets_from_connections(airbyte=airbyte_instance, connections=[stargazer_connection], key_prefix=["postgres"])

# preparing assets bassed on existing dbt project
dbt_assets = load_assets_from_dbt_project(project_dir=DBT_PROJECT_DIR, io_manager_key="db_io_manager", key_prefix="postgres")


# @asset(
#     description="The metabase dashboard where the stargazers are visualized",
#     metadata={"dashboard_url": "http://localhost:3000/dashboard/1-airbyte-sync-status"},
# )
# def metabase_dashboard(mart_gh_cumulative):
#     return "test"
