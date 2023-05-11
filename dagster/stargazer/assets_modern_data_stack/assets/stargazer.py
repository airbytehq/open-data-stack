from dagster import asset, op
from dagster_airbyte import (
    AirbyteManagedElementReconciler,
    airbyte_resource,
    AirbyteConnection,
    AirbyteSyncMode,
    load_assets_from_connections,
)
from dagster_airbyte.managed.generated.sources import (
    FakerSource,
    GithubSource,
    RssSource,
)
from dagster_airbyte.managed.generated.destinations import (
    LocalJsonDestination,
    PostgresDestination,
    DuckdbDestination,
)
from typing import List
from dagster_dbt import load_assets_from_dbt_project

import requests
import base64
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import os
import requests

import asyncio
import aiohttp
from sqlalchemy import schema
from ..utils.constants import DBT_PROJECT_DIR


AIRBYTE_PERSONAL_GITHUB_TOKEN = os.environ.get(
    "AIRBYTE_PERSONAL_GITHUB_TOKEN", "please-set-your-token"
)
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "please-set-your-token")

GNEW_API_KEY = os.environ.get("GNEW_API_KEY", "please-set-your-token")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "please-set-your-token")

# feed of DE
rss_list = [
    "https://www.theseattledataguy.com/feed/",
    "https://www.dataschool.io/rss/",
    # "ttps://roundup.getdbt.com/feed",
    # "http://feeds.feedburner.com/JamesSerra",
    # "https://pedram.substack.com/feed",
    # "http://www.gregreda.com/feeds/all.atom.xml",
    # "https://jpmonteiro.substack.com/feed",
    # "https://www.confessionsofadataguy.com/feed/",
    # "https://petrjanda.substack.com/feed",
    # "https://sarahsnewsletter.substack.com/feed",
    # "https://newsletter.pragmaticengineer.com/feed",
    # "https://stkbailey.substack.com/feed",
    # "https://benn.substack.com/feed",
    # "https://technically.substack.com/feed",
    # "https://sspaeti.com/index.xml",
    # "https://www.startdataengineering.com/index.xml",
    # "https://seattledataguy.substack.com/feed",
    # "https://dataproducts.substack.com/feed",
    # "https://blog.sqlauthority.com/feed/",
    # "https://www.dataengineeringweekly.com/feed",
    # "https://medium.com/feed/@maximebeauchemin",
    # "https://www.data-is-plural.com/feed.xml",
    # "https://davidsj.substack.com/feed",
    # "https://kentgraziano.com/feed/",
    # "https://fromanengineersight.substack.com/feed",
    # "https://groupby1.substack.com/feed",
    # "http://www.cathrinewilhelmsen.net/feed/",
    # "https://www.eckerson.com/feed/",
    # "https://joereis.substack.com/feed",
    # "https://medium.com/feed/@laurengreerbalik",
    # "https://www.winwithdata.io/feed",
    # "https://letters.moderndatastack.xyz/rss/",
    # "https://chollinger.com/blog/index.xml",
    # "https://mehdio.substack.com/feed",
    # "https://moderndata101.substack.com/feed",
    # "http://www.hansmichiels.com/feed/",
    # "https://agilebi.guru/feed/",
    # "https://medium.com/feed/@karimjdda",
    # "https://www.kahandatasolutions.com/blog.rss",
    # "https://semanticinsight.wordpress.com/feed/",
    # "http://www.tableausoftware.com/taxonomy/term/1920/feed",
    # "https://dataespresso.substack.com/feed",
    # "https://jonathanneo.substack.com/feed",
    # "https://vickiboykis.com/index.xml",
    # "https://ownyourdata.ai/wp/feed/",
]


def extract_domain(url: str) -> str:
    parsed_url = urlparse(url)
    # remove special character that are not allowed for dagster asset key
    cleaned_string = re.sub(
        r"[^A-Za-z0-9_]", "", parsed_url.netloc.replace("www.", "").replace(".", "_")
    )

    return cleaned_string


# pylint: redefined-builtin
from typing import List, Optional, Union
import dagster._check as check
from dagster._annotations import public
from dagster_airbyte.managed.types import GeneratedAirbyteSource


airbyte_instance = airbyte_resource.configured(
    {
        "host": "localhost",
        "port": "8000",
        "username": "airbyte",
        "password": {"env": "AIRBYTE_PASSWORD"},
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
    links = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href").startswith("https://github.com")
    ]
    # remove links that start with url
    links = [
        link
        for link in links
        if not link.startswith(url) and not link.endswith("github.com")
    ]
    # remove last slash if there
    links = [link[:-1] if link.endswith("/") else link for link in links]
    # remove repos without organization
    links = [link for link in links if len(link.split("/")) == 5]
    existings_links = asyncio.run(check_websites_exists(links))
    links = [link.replace("https://github.com/", "") for link in existings_links]

    # due to timeout limits while airbyte is checking each repo, I limited it here to make this demo work for you
    links = links[0:2]

    # return links as a string with blank space as separator
    return " ".join(links)


# test_data = FakerSource(name="test_data", count=100)

gh_awesome_de_list_source = GithubSource(
    name="gh_awesome_de_list",
    credentials=GithubSource.PATCredentials(AIRBYTE_PERSONAL_GITHUB_TOKEN),
    start_date="2020-01-01T00:00:00Z",
    # repository=get_awesome_repo_list(),  # "prometheus/haproxy_exporter",
    repository="prometheus/haproxy_exporter",
    page_size_for_large_streams=100,
)

# postgres_destination = PostgresDestination(
#     name="postgres",
#     host="localhost",
#     port=5432,
#     database="postgres",
#     schema="public",
#     username="postgres",
#     password=POSTGRES_PASSWORD,
#     ssl_mode=PostgresDestination.Disable(),
# )


# stargazer_connection = AirbyteConnection(
#     name="fetch_stargazer",
#     source=gh_awesome_de_list_source,
#     destination=postgres_destination,
#     stream_config={"stargazers": AirbyteSyncMode.incremental_append()},
#     normalize_data=False,
# )


# test_connection = AirbyteConnection(
#     name="fetch_test_data_duckdb",
#     source=test_data,
#     destination=duckdb_destination,
#     stream_config={
#         "_airbyte_raw_users": AirbyteSyncMode.full_refresh_overwrite(),
#         "_airbyte_raw_products": AirbyteSyncMode.full_refresh_overwrite(),
#     },
#     normalize_data=False,  # True,
# )

json_awesome_de_list = LocalJsonDestination(
    name="json_awesome_de_list",
    destination_path=f"/local/ods/json_awesome_de_list/",
)

duckdb_destination = DuckdbDestination(
    name="duckdb",
    path="/local/ods/stage.db",
)

stargazer_connection = AirbyteConnection(
    name="fetch_stargazer_duckdb",
    source=gh_awesome_de_list_source,
    destination=json_awesome_de_list,  # duckdb_destination,
    stream_config={"stargazers": AirbyteSyncMode.incremental_append()},
    normalize_data=False,
)


# ###############################
# # simple pattern analysis
# ###############################


repo_connection = AirbyteConnection(
    name="fetch_stargazer_duckdb",
    source=gh_awesome_de_list_source,
    destination=duckdb_destination,
    stream_config={
        "repositories": AirbyteSyncMode.incremental_append(),
        "stargazers": AirbyteSyncMode.incremental_append(),
    },
    normalize_data=False,  # True,
)


@op
def fetch_readme(repos: list) -> dict:

    GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "token {}".format(GITHUB_API_TOKEN),
    }

    matches_dict = {}

    for repo in repos:

        url = "https://api.github.com/repos/{}/readme".format(repo)

        response = requests.get(url, headers=headers)
        content = response.json()["content"]

        # Decode base64 content
        readme_content = base64.b64decode(content).decode("utf-8")

        # Extract links and names using regex
        pattern = r"\* \[(.+?)\]\((.+?)\)"
        matches = re.findall(pattern, readme_content)

        for match in matches:
            name, link = match
            matches_dict[name] = link

            print(f"Name: {name}\nLink: {link}\n")

    return matches_dict


def create_rss_airbyte_connection(name: str, rss_url: str):
    rss_source = RssSource(name=f"rss_{name}", url=rss_url)
    json_destination = LocalJsonDestination(
        name=f"json_{name}",
        destination_path=f"/local/ods/json_export/{name}.jsonl",
    )

    connection = AirbyteConnection(
        name=f"fetch_{name}",
        source=rss_source,
        destination=json_destination,  # duckdb_destination: Would need to handle JSONL format, for now it will through an "Invalid JSON" error
        stream_config={"items": AirbyteSyncMode.full_refresh_overwrite()},
        normalize_data=False,
        prefix=f"{name}_",
    )
    return connection


rss_connections = []
for i, rss_url in enumerate(rss_list):
    readable_name = extract_domain(rss_url)

    i = create_rss_airbyte_connection(readable_name, rss_url)
    rss_connections.append(i)

# @asset(
#     description="The metabase dashboard where the stargazers are visualized",
#     metadata={"dashboard_url": "http://localhost:3000/dashboard/1-airbyte-sync-status"},
# )
# def metabase_dashboard(mart_gh_cumulative):
#     return "test"


# ##################################
# Dagster Reconciler
# ##################################

airbyte_reconciler = AirbyteManagedElementReconciler(
    airbyte=airbyte_instance,
    connections=rss_connections + [stargazer_connection],
    delete_unmentioned_resources=True,
)

# load airbyte connection from above pythonic definitions
airbyte_assets = load_assets_from_connections(
    airbyte=airbyte_instance,
    connections=[stargazer_connection] + rss_connections,
    key_prefix=["ods"],
)

# preparing assets bassed on existing dbt project
dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_DIR,
    io_manager_key="db_io_manager",
    key_prefix=["ods"],
)
