# Day 38 complete zone structure

Account: stderoadmapdvrr26

Raw preserves the original files:
- raw/covid/owid-covid-data.csv
- raw/orders_json/orders.json
- raw/orders_json/customers.json

Silver contains validated records:
- staging/covid/uk/owid-covid-uk.parquet (Day 37)
- staging/orders/orders_clean.parquet (Day 38)

Gold contains defined aggregates:
- curated/covid/uk/monthly_cases.parquet
- curated/orders/sales_by_city.parquet

Run:
- activate .venv
- set STORAGE_KEY
- python day38_zones.py

Independent check:
- python validate_day38.py

Checks:
- required fields
- unique keys
- valid customer join
- reconciled totals
- uploaded Parquet read-back equality

Metric meaning:
- monthly_cases.parquet sums available reported new_cases by country and month
- observed_days measures days with reported new_cases
- entirely missing months remain null
- sales_by_city.parquet groups by city
- sample sales: 2 orders, 3 units, 940.00 total sales

Reruns overwrite derived paths. Multi-file writes are not atomic.

ADF orchestration is planned for Days 39 onward.
