# Unified Afficionado Coffee Roasters

This repository contains a Streamlit-based business intelligence dashboard for Afficionado Coffee Roasters. It analyzes transactional sales data to uncover patterns in revenue, product demand, time-of-day behavior, store performance, and statistical insights.

## Project Overview

The dashboard helps management understand:
- Sales trends over time
- Peak and low-traffic hours and days
- Store-to-store performance differences
- Product category and product type mix
- Statistical patterns and actionable insights

## Features

- Interactive filtering by store, month, day, hour, category, and product type
- KPI summary cards for revenue, transactions, quantity sold, and average order value
- Sales trend analysis with moving averages
- Time-based and day-based performance analysis
- Store comparison dashboards
- Statistical analysis for key business questions
- Executive-style insights and recommendations

## Repository Structure

- app.py — Main Streamlit application entry point
- dashboard/ — UI components and styling
- src/ — Data preprocessing, KPI calculations, and analytics logic
- Dataset/ — Raw and processed transaction datasets
- reports/ — Executive summary, data quality report, and research paper materials
- requirements.txt — Python dependencies

## Setup

1. Clone the repository
2. Create and activate a Python environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the dashboard:

```bash
streamlit run app.py
```

## Data

The dashboard expects the processed dataset at:

- Dataset/Processed dataset/Afficionado_Coffee_Processed.csv

If the file location differs on your machine, update the dataset path in app.py accordingly.

## Notes

This project was developed as an academic/business analytics capstone and is intended for exploratory analysis and decision support.
