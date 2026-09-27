# Day 36 data lake architecture

```mermaid
flowchart TD
    A[OWID COVID CSV] --> E[Azure Data Factory]
    B[Open Meteo JSON] --> E
    C[REST Countries JSON] --> E
    D[Orders and customers JSON] --> E
    E --> F[raw container  Bronze]
    F --> G[Databricks or PySpark validation]
    G --> H[staging container  Silver]
    H --> I[Databricks or SQL aggregation]
    I --> J[curated container  Gold]
    J --> K[Power BI SQL and business users]
```

- ADF orchestrates ingestion and dependencies.
- ADLS Gen2 stores Bronze, Silver and Gold.
- Databricks or PySpark validates and transforms.
- Gold supplies governed analytics outputs.
