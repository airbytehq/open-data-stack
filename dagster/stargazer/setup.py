from setuptools import find_packages, setup

setup(
    name="assets_modern_data_stack",
    packages=find_packages(exclude=["assets_modern_data_stack_tests"]),
    package_data={"assets_modern_data_stack": ["transformation_dbt/*"]},
    install_requires=[
        "dagster",
        "dagster-airbyte",
        "dagster-managed-elements",
        "dagster-dbt",
        "dagster-postgres",
        "pandas",
        "numpy",
        "scipy",
        "dbt-core",
        "dbt-postgres",
        "aiohttp",
        "requests",
        "beautifulsoup4",
        "dbt-duckdb==1.4.0",
        "duckdb==0.7.0",  # this must be aligned with the `destination-duckdb` version of airbyte, otherwise stage.db can't be opened!
    ],
    extras_require={"dev": ["dagit", "pytest", "black"]},
)
