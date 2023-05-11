# Open Data Stack Projects

The idea is to have an extendable repository for reference projects with the [Open Data Stack](https://glossary.airbyte.com/term/open-data-stack/). It should be possible to add different BI tools or another orchestrator.

So far, this repo contains different these two projects:
- Open Data Stack with Airbyte, dbt, dagster, Metabase: [Configure Airbyte Connections with Python (Dagster)](https://airbyte.com/tutorials/configure-airbyte-with-python-dagster)
  - The project scrapes the [Awesome Data Engineering List](https://github.com/igorbarinov/awesome-data-engineering) links with Beautiful Soup and ingested the stars from each GitHub repository to a Postgres database—seeing the trends for each in Metabase.
  - You can also check why each of the tools has been chosen in [The Open Data Stack Distilled into Four Core Tools](https://airbyte.com/blog/modern-open-data-stack-four-core-tools)
- Open Data Stack with dbt and Metabase: [Use-Case: Airbyte Monitoring](https://airbyte.com/blog/airbyte-monitoring-with-dbt-and-metabase)
  - In this project, you learn how to implement an Airbyte monitoring dashboard with dbt and Metabase on a locally deployed Airbyte instance. It will allow you to get an operational view of your current running data ingestions and a high-level overview of what happened in the past.

Future potential use cases have been listed in an inial [series](https://airbyte.com/blog/building-airbytes-data-stack) on how we built the data stack at Airbyte.

---
The Open Data Stack is a "better" term for the [Modern Data Stack](https://glossary.airbyte.com/term/modern-data-stack/) that focuses on solutions built on open-source and open standards covering the [Data Engineering Lifecycle](https://glossary.airbyte.com/term/data-engineering-lifecycle/). Companies can reuse existing battle-tested solutions and build on them instead of reinventing the wheel by re-implementing critical components for each component of the data stack. 

*Open* is so important and often overlooked because it embeds the data stack with tools from the open data stack, such as Airbyte, dbt, Dagster, Superset, Rill, and many more. Unlike closed-source services, it lets you integrate them into your services or products.
