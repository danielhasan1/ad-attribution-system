# Ad Attribution System

A production-grade data engineering solution for multi-channel advertising attribution and budget optimization.

## Problem Statement

Marketing teams waste 30-50% of ad budgets on underperforming channels due to lack of proper attribution modeling. This system provides real-time attribution analysis and automated budget reallocation recommendations.

## Architecture

- **Data Sources**: Facebook Ads API, Google Ads API
- **Processing**: Real-time ETL pipelines with Apache Airflow
- **Storage**: PostgreSQL for structured data, optimized for analytics queries
- **Attribution**: Multi-touch attribution models (Last-touch, First-touch, Linear, Markov Chain)
- **Visualization**: Real-time dashboards with actionable insights

## Features

- Multi-channel data ingestion (Facebook, Google Ads)
- Real-time attribution modeling
- Budget optimization recommendations
- Performance monitoring and alerting
- Interactive analytics dashboard

## Tech Stack

- **Language**: Python 3.9+
- **Database**: PostgreSQL 17
- **ETL**: Apache Airflow, Pandas
- **APIs**: Facebook Marketing API, Google Ads API
- **Dashboard**: Streamlit
- **Deployment**: Docker

## Setup

```bash