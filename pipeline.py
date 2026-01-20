from dagster import (
    op,
    job,
    get_dagster_logger,
    Failure,
    ScheduleDefinition
)

import subprocess
import sys
from pathlib import Path

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
DBT_DIR = PROJECT_ROOT / "medical_warehouse"

# ------------------------------------------------------------------
# Ops
# ------------------------------------------------------------------

@op
def scrape_telegram_data():
    logger = get_dagster_logger()
    logger.info("Starting Telegram scraping")

    try:
        result = subprocess.run(
            [sys.executable, "src/scraper.py"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        return "Scraping completed"

    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)
        raise Failure("Telegram scraping failed")


@op
def load_raw_to_postgres():
    logger = get_dagster_logger()
    logger.info("Loading raw JSON data into PostgreSQL")

    try:
        result = subprocess.run(
            [sys.executable, "src/load_raw_to_postgres.py"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        return "Raw data loaded"

    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)
        raise Failure("Raw data load failed")


@op
def run_dbt_transformations():
    logger = get_dagster_logger()
    logger.info("Running dbt transformations")

    try:
        result = subprocess.run(
            ["dbt", "run"],
            cwd=DBT_DIR,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        return "dbt models built"

    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)
        raise Failure("dbt transformations failed")


@op
def run_yolo_enrichment():
    logger = get_dagster_logger()
    logger.info("Running YOLO image enrichment")

    try:
        result = subprocess.run(
            [sys.executable, "src/yolo_detect.py"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        return "YOLO enrichment completed"

    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)
        raise Failure("YOLO enrichment failed")

# ------------------------------------------------------------------
# Job Graph
# ------------------------------------------------------------------

@job
def medical_telegram_pipeline():
    scrape_telegram_data()
    load_raw_to_postgres()
    run_dbt_transformations()
    run_yolo_enrichment()

# ------------------------------------------------------------------
# Schedule (Daily)
# ------------------------------------------------------------------

daily_schedule = ScheduleDefinition(
    job=medical_telegram_pipeline,
    cron_schedule="0 2 * * *"  # runs daily at 02:00
)
