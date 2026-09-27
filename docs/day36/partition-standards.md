# Day 36 folder and partition standards

## Purpose

These standards define predictable ADLS Gen2 paths for the Bronze, Silver and Gold layers. Consistent paths support parameterized pipelines, filtered reads, replay, troubleshooting and data governance.

## General naming rules

- Use lowercase directory and file names.
- Use snake_case for names containing multiple words.
- Use key=value format for partition directories.
- Use four digits for years: YYYY.
- Use two digits for months: MM.
- Use two digits for days: DD.
- Partition only by stable fields that are commonly used as filters.
- Avoid creating many partitions containing only one or two small files.
- Do not use spaces in directory names.

## Bronze standard

Pattern:

```text
raw/<source>/<entity>/ingestion_year=YYYY/ingestion_month=MM/ingestion_day=DD/
                                                                                                                                                                                                    
                                                                                                                                                                           ```

## Silver standard

Pattern:

```text
staging/<domain>/<entity>/year=YYYY/month=MM/
```

Purpose:

- Stores validated and cleaned detailed records.
- Supports commonly used year and month filters.
- Provides reusable data for engineering and analytics.

COVID example:

```text
staging/health/covid/year=2026/month=09/
```

Weather example:

```text
staging/weather/weather_observations/year=2026/month=09/
```

Orders example:

```text
staging/sales/orders/year=2026/month=09/
```

## Gold standard

Pattern:

```text
curated/<domain>/<data_product>/year=YYYY/month=MM/
```

Purpose:

- Stores business-ready aggregates and dimensions.
- Organizes outputs by business domain and data product.
- Supports reporting filters and governed analytics.

COVID example:

```text
curated/health/daily_cases_by_country/year=2026/month=09/
```

Weather example:

```text
curated/weather/average_temperature_by_city/year=2026/month=09/
```

Orders example:

```text
curated/sales/revenue_by_day/year=2026/month=09/
```
 ## Small-file rule

Do not partition a small practice dataset by year, month, day, country and city simultaneously. Excessive partitioning creates many small files and increases listing and processing overhead.

For small datasets, use year and month only. Add a daily partition only when the data volume and query pattern justify it.
