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

---

## 🔜 Next Steps

* **Task 3:** Data enrichment using YOLO (object detection on images)
* **Task 4:** Analytical API using FastAPI
* **Task 5:** Pipeline orchestration and CI/CD
