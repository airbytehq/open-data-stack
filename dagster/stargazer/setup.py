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
    ],
    extras_require={"dev": ["dagit", "pytest", "black"]},
)
