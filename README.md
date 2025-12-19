
#  E-Commerce Data Engineering Pipeline  
**Prefect • AWS S3 • Docker • Python**

---

##  Project Overview
This project implements an **end-to-end batch Data Engineering pipeline** for e-commerce data using **Prefect for orchestration** and **AWS S3 as a data lake**.

The pipeline is designed with **production-oriented architecture**, covering:
- Raw data ingestion
- Data cleaning & transformation
- Business metrics generation
- Cloud storage integration
- Workflow orchestration
- Containerized execution

---

## Flow

```

CSV Data Sources
│
▼
AWS S3 (Raw Zone)
raw-data/
│
▼
Prefect Orchestration
ecommerce_etl_pipeline
│
▼
Data Processing Layer
(Pandas Transformations)
│
▼
Business Metrics Layer
│
▼
AWS S3 (Processed Zone)
processed/
└── metrics/

```

---

##  Architecture Layers

### 🔹 Data Source Layer
- CSV files representing e-commerce entities:
  - customers
  - products
  - orders
  - order_items
  - reviews

---

### 🔹 Data Lake Layer (AWS S3)
The project follows a **simplified Medallion Architecture**:

| Layer | S3 Path | Description |
|-----|--------|------------|
| Raw | `raw-data/` | Immutable raw data |
| Processed | `processed/` | Cleaned & enriched datasets |
| Metrics | `processed/metrics/` | Business-ready analytics |

---

### 🔹 Orchestration Layer (Prefect)
- Manages task dependencies
- Automatic retry & failure handling
- Centralized logging and observability
- Supports local and containerized execution

---

### 🔹 Processing Layer
- Data cleaning and normalization
- Feature engineering
- Time-based transformations
- Schema enrichment

---

### 🔹 Business Metrics Layer
This layer generates analytics-ready datasets:
- Customer Lifetime Value
- Product performance metrics
- Monthly sales trends

---

##  Project Structure

```

data-pipeline/
│
├── config/
│   ├── aws_config.yaml
│   └── prefect_config.yaml
│
├── infrastructure/
│   └── docker/
│       └── Dockerfile
│
├── src/
│   ├── data_ingestion/
│   │   └── s3_uploader.py
│   │
│   ├── data_processing/
│   │   └── data_processing.py
│   │
│   ├── orchestration/
│   │   └── prefect_flow.py
│
├── tests/
│   ├── prefect_test.py
│   └── test_aws_connection.py
│
├── data/
│   └── raw/
│
├── docker-compose.yml
├── requirements.txt
├── prefect.yaml
└── README.md

````

---

##  Pipeline Flow
1. Download raw data from AWS S3
2. Clean and transform datasets
3. Generate business metrics
4. Upload processed data back to S3
5. Orchestrate execution using Prefect

---

##  Tech Stack

| Component | Technology |
|---------|-----------|
| Language | Python |
| Orchestration | Prefect |
| Storage | AWS S3 |
| Processing | Pandas |
| Containerization | Docker |

---

##  Setup & Installation

### Clone Repository
```bash
git clone https://github.com/bintangfajarr/de-course-handson.git
cd de-course-handson/data-pipeline
````

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Environment Variables

Create a `.env` file:

```env
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

---

##  Running the Pipeline

### Start Prefect Server

```bash
prefect server start
```

### Execute the Flow

```bash
python src/orchestration/prefect_flow.py
```

---

##  Run with Docker

```bash
docker-compose up
```

---

##  Key Features

* Modular ETL pipeline design
* Fault-tolerant task orchestration
* Business metrics generation
* Cloud-native data lake architecture
* Production-ready project structure

---

##  Future Enhancements

* Data quality validation
* Spark-based large-scale processing
* Data warehouse integration (Redshift / BigQuery)
* CI/CD automation
* dbt metrics layer
---


