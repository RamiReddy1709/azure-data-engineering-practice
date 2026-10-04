# Day 38 complete zone structure diagram

```mermaid
flowchart TD
  subgraph Raw["Raw container"]
    R1["raw/covid/owid-covid-data.csv"]
    R2["raw/orders_json/orders.json"]
    R3["raw/orders_json/customers.json"]
  end

  subgraph Silver["Staging container - Silver"]
    S1["staging/covid/uk/owid-covid-uk.parquet"]
    S2["staging/orders/orders_clean.parquet"]
  end

  subgraph Gold["Curated container - Gold"]
    G1["curated/covid/uk/monthly_cases.parquet"]
    G2["curated/orders/sales_by_city.parquet"]
  end

  D37["Day 37 Python"]
  D38C["Day 38 Python monthly aggregate"]
  D38O["Day 38 clean and join"]
  D38G["Group by city"]
  ADF["ADF orchestration planned for Days 39 onward"]

  R1 --> D37 --> S1 --> D38C --> G1
  R2 --> D38O
  R3 --> D38O
  D38O --> S2 --> D38G --> G2
  ADF -.-> D37
  ADF -.-> D38O
```

## Implemented paths

Raw:
- raw/covid/owid-covid-data.csv
- raw/orders_json/orders.json
- raw/orders_json/customers.json

Silver:
- staging/covid/uk/owid-covid-uk.parquet
- staging/orders/orders_clean.parquet

Gold:
- curated/covid/uk/monthly_cases.parquet
- curated/orders/sales_by_city.parquet

ADF orchestration is planned for Days 39 onward.
