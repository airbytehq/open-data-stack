from dagster import asset, op, with_resources
from dagster_airbyte import load_assets_from_airbyte_project, AirbyteManagedElementReconciler, airbyte_resource, AirbyteConnection, AirbyteSyncMode
from dagster_airbyte.managed.generated.sources import GithubSource
from dagster_airbyte.managed.generated.destinations import LocalJsonDestination
from typing import List, Mapping

from bs4 import BeautifulSoup
import os
import requests

from ..utils.constants import AIRBYTE_CONNECTION_ID, DBT_PROJECT_DIR


TOKEN = os.environ.get("AIRBYTE_PERSONAL_GITHUB_TOKEN", "please-set-your-token")


airbyte_instance = airbyte_resource.configured(
    {
        "host": "localhost",
        "port": "8000",
        "username": "airbyte",
        "password": {"env": "AIRBYTE_PASSWORD"},
    }
)

# airbyte_assets = load_assets_from_airbyte_project(
#     project_dir="../../../../airbyte/test",
# )

# airbyte_assets = with_resources(
#     [load_assets_from_airbyte_project(project_dir="path/to/airbyte/project")],
#     {"airbyte": airbyte_instance},
# )


gh_awesome_de_list_source = GithubSource(
    name="gh_awesome_de_list",
    credentials=GithubSource.PATCredentials(TOKEN),
    start_date="2020-10-01T00:00:00Z",
    repository="prometheus/haproxy_exporter",
    page_size_for_large_streams=10,
)

local_json_destination = LocalJsonDestination(
    name="local-json",
    destination_path="/local/cereals_out.json",
)

stargazer_connection = AirbyteConnection(
    name="fetch_stargazer",
    source=gh_awesome_de_list_source,
    destination=local_json_destination,
    stream_config={"fetch_stargazer": AirbyteSyncMode.full_refresh_overwrite()},
    # stream_config={"fetch-stargazer": AirbyteSyncMode.FULL_REFRESH_OVERWRITE},
)
airbyte_reconciler = AirbyteManagedElementReconciler(
    airbyte=airbyte_instance,
    connections=[stargazer_connection],
)

# dbt_assets = load_assets_from_dbt_project(project_dir=DBT_PROJECT_DIR, io_manager_key="db_io_manager")


@op
def get_awesome_repo_list() -> List[str]:

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
    # remove `https://github.com/` from links
    links = [link.replace("https://github.com/", "") for link in links]

    return links
