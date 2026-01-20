# 🏥 Medical Telegram Data Warehouse

**Kara Solutions – Data Engineering Project**

## 📌 Project Overview

This project builds an **end-to-end data platform** that transforms unstructured Telegram data from Ethiopian medical and pharmaceutical channels into a **clean, analytics-ready data warehouse**.

The platform follows a **modern ELT architecture**:

* **Extract & Load** raw data into a data lake and PostgreSQL
* **Transform** data inside the warehouse using **dbt**
* Model data into a **dimensional star schema** optimized for analysis
* Lay the foundation for downstream enrichment (YOLO) and analytics APIs (FastAPI)

---

## 🧩 Task 1 – Data Scraping and Collection (Extract & Load)

### 🎯 Objective

Extract messages and images from public Telegram channels related to medical and pharmaceutical businesses in Ethiopia and store them in a **raw data lake** while preserving the original data structure.

---

### 📥 Data Sources

Public Telegram channels including:

* **CheMed** – Medical products
* **Lobelia Cosmetics** – Cosmetics and health products
* **Tikvah Pharma** – Pharmaceuticals
* **Raya Pharmaceuticals**
* **Cafimad**
* **New Optics**
* **Vimax**
* Additional channels from *et.tgstat.com/medicine*

---

### 🛠️ Implementation

* **Library:** Telethon (Telegram API)
* **Authentication:** Personal Telegram account (session-based)
* **Approach:** Modular, config-driven scraping pipeline

---

### 📂 Raw Data Lake Structure

```text
data/raw/
├── telegram_messages/
│   └── YYYY-MM-DD/
│       ├── CheMed123.json
│       ├── lobelia4cosmetics.json
│       └── tikvahpharma.json
└── images/
    └── channel_name/
        └── message_id.jpg
```

---

### 🧾 Extracted Fields

* `message_id`
* `channel_name`
* `message_date`
* `message_text`
* `has_media`
* `image_path`
* `views`
* `forwards`

---

### 📋 Logging & Reliability

* Logs scraping progress and failures
* Handles:

  * Rate limits
  * Network issues
  * Invalid messages
* Logs stored under `logs/`
* Clear **success/failure confirmation** on completion

---

### ✅ Deliverables

* `src/scraper.py`
* Raw JSON files stored in the data lake
* Images downloaded and organized by channel
* Logs capturing scraping activity

---

## 🧩 Task 2 – Data Modeling and Transformation (Transform)

### 🎯 Objective

Transform raw Telegram data into a **clean, structured data warehouse** using **PostgreSQL + dbt**, enabling trusted analytics and reporting.

---

### 🏗️ Architecture

```text
Telegram → Data Lake (JSON)
         → PostgreSQL (raw schema)
         → dbt Staging Models
         → dbt Mart Models (Star Schema)
```

---

### 🗄️ Raw Data Load (PostgreSQL)

A Python batch script:

* Reads raw JSON files from the data lake
* Loads data into PostgreSQL under the `raw` schema
* Creates table:

```sql
raw.telegram_messages
```

* Preserves original message payload using `JSONB`

📄 Script:

```text
scripts/load_raw_to_postgres.py
```

---

### 🔧 dbt Transformation Layer

#### 1️⃣ Staging Models (`models/staging/`)

Purpose:

* Clean and standardize raw data
* Enforce naming conventions
* Prepare data for dimensional modeling

Key transformations:

* Type casting (timestamps, integers)
* Null filtering
* Derived fields:

  * `message_length`
  * `has_image`

Example:

```text
stg_telegram_messages.sql
```

---

#### 2️⃣ Dimensional Star Schema (`models/marts/`)

##### 📐 Dimension Tables

**dim_channels**

* channel_key (surrogate key)
* channel_name
* channel_type
* first_post_date
* last_post_date
* total_posts
* avg_views

**dim_dates**

* date_key
* full_date
* day_of_week, day_name
* week_of_year
* month, month_name
* quarter, year
* is_weekend

---

##### 📊 Fact Table

**fct_messages**

* message_id
* channel_key (FK)
* date_key (FK)
* message_text
* message_length
* view_count
* forward_count
* has_image

---

### 🧪 Data Quality & Testing

Implemented using dbt tests:

* `unique` and `not_null` tests on primary keys
* `relationships` tests on foreign keys

Custom tests:

* `assert_no_future_messages.sql`
* `assert_positive_views.sql`

All tests must return **zero rows** to pass.

---

### 📚 Documentation

* Generated using:

```bash
dbt docs generate
dbt docs serve
```

* Includes:

  * Model descriptions
  * Column-level documentation
  * Lineage graphs

---

### ✅ Deliverables

* Fully configured dbt project (`medical_warehouse`)
* Staging and mart models
* Passing dbt tests
* Generated dbt documentation
* Clear star schema design rationale



## Task 3 – Data Enrichment with Object Detection (YOLO)

### Objective

Use computer vision to analyze images scraped from Telegram channels and integrate the findings into the data warehouse to gain additional insights.

### Implementation

1. **YOLO Environment Setup**

   * Installed the `ultralytics` package and used the YOLOv8 nano model (`yolov8n.pt`) for efficient image detection on standard hardware.
   * YOLO detects general objects such as bottles and people, providing analytical value even without domain-specific training.

2. **Object Detection Script**

   * Implemented in `src/yolo_detect.py`.
   * The script scans all images downloaded during Task 1.
   * For each image, YOLO detects objects and records the **object class**, **confidence score**, and a **categorical label** based on the content:

     * `promotional` → person + product
     * `product_display` → product only
     * `lifestyle` → person only
     * `other` → neither detected
   * Added `channel_key` from the source channel to each record for later integration.

3. **Detection Results**

   * Results stored as a **CSV file** in `data/processed/yolo_detection.csv`.
   * CSV columns: `message_id`, `channel_key`, `date_key`, `detected_class`, `confidence_score`, `image_category`.

4. **Integration with Data Warehouse**

   * Created a new DBT model: `models/marts/fct_image_detections.sql`.
   * Loaded YOLO detection results into PostgreSQL and joined with `fct_messages` using `message_id`.
   * This allowed enriched analytics, such as correlating post type (`promotional` vs `product_display`) with views.

5. **Analysis and Insights**

   * "Promotional" posts (person + product) generally received higher average views than "product_display" posts.
   * Channels such as `CheMed123` and `Vimax123` utilized more visual content than others.
   * **Limitations**: Pre-trained YOLO models do not detect specific product names or local Ethiopian pharmaceuticals; some detections may be incorrect or incomplete for domain-specific objects.

### Deliverables

* `src/yolo_detect.py` → Object detection script
* `data/processed/yolo_detection.csv` → Detection results
* `models/marts/fct_image_detections.sql` → DBT model integrating YOLO results
* Analytical insights documented in this README

---

## Task 4 – Analytical API

### Objective

Expose the data warehouse through a REST API using FastAPI, allowing stakeholders to query key business metrics programmatically.

### Implementation

1. **Project Structure**

   * `api/main.py` → All FastAPI endpoints
   * `api/database.py` → SQLAlchemy database connection and session management
   * `api/schemas.py` → Pydantic models for request and response validation

2. **Endpoints Implemented**

   * **Top Products:** `/api/reports/top-products?limit=10` → Returns the most frequently mentioned products.
   * **Channel Activity:** `/api/channels/{channel_name}/activity` → Returns posting volume, trends, and engagement metrics.
   * **Message Search:** `/api/search/messages?query=<keyword>&limit=20` → Keyword-based message search.
   * **Visual Content Stats:** `/api/reports/visual-content` → Statistics about image usage across channels (counts and ratios).

3. **Validation and Error Handling**

   * Pydantic models enforce correct request/response structures.
   * All endpoints return proper HTTP status codes and descriptive error messages.

4. **Documentation**

   * Auto-generated OpenAPI docs available at `/docs`.
   * Allows testing endpoints interactively.

### Deliverables

* FastAPI application (`api/main.py`) with 4 analytical endpoints
* Pydantic schemas (`api/schemas.py`)
* OpenAPI documentation at `/docs`

---

## Task 5 – Pipeline Orchestration

### Objective

Automate the entire pipeline using Dagster, enabling reproducible, observable, and schedulable execution of ETL, DBT transformations, YOLO enrichment, and API exposure.

### Implementation

1. **Dagster Setup**

   * Installed `dagster` and `dagster-webserver`.
   * Defined a pipeline (`pipeline.py`) composed of these ops:

     * `scrape_telegram_data` → Run scraper from Task 1
     * `load_raw_to_postgres` → Load raw JSON into PostgreSQL
     * `run_dbt_transformations` → Execute DBT models from Task 2
     * `run_yolo_enrichment` → Run YOLO detection from Task 3

2. **Job Graph**

   * Ops are connected in a dependency graph to ensure correct execution order.

3. **Execution**

   * Launch via `dagster dev -f pipeline.py`
   * Monitor pipeline runs, logs, and status using **Dagster UI**: [http://localhost:3000](http://localhost:3000)

4. **Scheduling and Alerts**

   * Configured daily runs with automatic logging and alerting on failures.

### Deliverables

* `pipeline.py` → Dagster pipeline definition
* Dagster UI screenshots showing successful execution

---

## 🚀 Running the FastAPI API

### Local (recommended)

From the project root:

```bash
uvicorn api.main:app --reload
```

Then open:

- **Docs UI (Swagger)**: `http://127.0.0.1:8000/docs`
- **Root health/info**: `http://127.0.0.1:8000/`

If you see `{"detail":"Not Found"}`, it usually means you’re visiting a path that doesn’t exist (for example `http://127.0.0.1:8000/api`), or you started a different module than `api.main:app`.