from dagster import asset, op, with_resources
from dagster_airbyte import load_assets_from_airbyte_project, AirbyteManagedElementReconciler, airbyte_resource, AirbyteConnection, AirbyteSyncMode
from dagster_airbyte.managed.generated.sources import GithubSource
from dagster_airbyte.managed.generated.destinations import LocalJsonDestination, PostgresDestination
from typing import List, Mapping, Union

from bs4 import BeautifulSoup
import os
import requests

import asyncio
import aiohttp
from ..utils.constants import AIRBYTE_CONNECTION_ID, DBT_PROJECT_DIR


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
    repository=get_awesome_repo_list(),  # "prometheus/haproxy_exporter",
    # repository="sindresorhus/awesome rqlite/rqlite pingcap/tidb pinterest/mysql_utils rescrv/HyperDex iondbproject/iondb filodb/FiloDB rain1017/memdb twitter-archive/flockdb gchq/Gaffer influxdata/influxdb OpenTSDB/opentsdb kairosdb/kairosdb spotify/heroic akumuli/Akumuli dalmatinerdb/dalmatinerdb rackerlabs/blueflood NationalSecurityAgency/timely tarantool/tarantool greenplum-db/gpdb cayleygraph/cayley confluentinc/bottledwater-pg airbnb/kafkat xstevens/pg_kafka edenhill/librdkafka wurstmeister/kafka-docker SOHU-Co/kafka-node pinterest/secor uber/kafka-logger mozilla-services/heka spotify/snakebite RaRe-Technologies/smart_open tuplejump/snackfs-release s3ql/s3ql google/snappy protocolbuffers/protobuf EsotericSoftware/kryo pipelinedb/pipelinedb faust-streaming/faust hstreamdb/hstream Stratio/deep-spark asavinov/bistro apache/incubator-hivemall dropbox/PyHive stitchfix/pyxley plotly/dash metabase/metabase spotify/luigi apache/airflow pinterest/pinball dagster-io/dagster treeverse/lakeFS pblittle/docker-logstash jprante/elasticsearch-jdbc zombodb/zombodb redbooth/gockerize weaveworks/weave CenturyLinkLabs/zodiac google/cadvisor figadore/micro-s3-persistence grammarly/rocker-compose hashicorp/nomad Interana/eventsim prometheus/prometheus prometheus/haproxy_exporter",
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

# dumym that `dagster-me` with new pythonic airbyte configs works
@asset
def dummy() -> str:
    return "test"


# dbt_assets = load_assets_from_dbt_project(project_dir=DBT_PROJECT_DIR, io_manager_key="db_io_manager")
