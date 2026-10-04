from io import BytesIO
import json
import pandas as pd
import os
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceExistsError

ACCOUNT = "stderoadmapdvrr26"
service = DataLakeServiceClient(
    account_url=f"https://{ACCOUNT}.dfs.core.windows.net",
    credential=AzureNamedKeyCredential(ACCOUNT, os.environ["STORAGE_KEY"]),
)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_bytes(zone, path):
    return service.get_file_client(zone, path).download_file().readall()

def read_parquet(zone, path):
    return pd.read_parquet(BytesIO(read_bytes(zone, path)))

def read_json(path):
    data = json.loads(read_bytes("raw", path).decode("utf-8-sig"))
    require(isinstance(data, list) and len(data) > 0,
            f"Expected nonempty JSON array: {path}")
    return pd.DataFrame(data)

def write_parquet(zone, path, frame):
    fs = service.get_file_system_client(zone)
    parts = path.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        directory = fs.get_directory_client("/".join(parts[:i]))
        try:
            directory.create_directory()
        except ResourceExistsError:
            pass
    payload = BytesIO()
    frame.to_parquet(payload, index=False, compression="snappy")
    client = fs.get_file_client(path)
    client.upload_data(payload.getvalue(), overwrite=True)
    actual = read_parquet(zone, path)
    pd.testing.assert_frame_equal(frame.reset_index(drop=True), actual)
    require(client.get_file_properties().size > 0, "Empty output file")
    print(f"PASS | {zone}/{path} | {len(actual)} rows")

def positive_int(frame, column):
    values = pd.to_numeric(frame[column], errors="raise")
    require(values.notna().all() and (values > 0).all()
            and (values % 1 == 0).all(), f"Invalid {column}")
    frame[column] = values.astype("int64")
def build_outputs():
    covid = read_parquet("staging", "covid/uk/owid-covid-uk.parquet")
    require(not covid.empty, "Complete Day 37 first")
    require({"country", "date", "new_cases"}.issubset(covid.columns),
            "COVID Silver schema does not match Day 37")
    require(covid["country"].notna().all()
            and covid["country"].eq("United Kingdom").all(),
            "Unexpected country")
    covid["date"] = pd.to_datetime(covid["date"], errors="raise")
    require(covid["date"].notna().all(), "Missing dates")
    require(not covid.duplicated(["country", "date"]).any(),
            "Duplicate COVID dates; correct Day 37 output first")
    covid["new_cases"] = pd.to_numeric(covid["new_cases"], errors="raise")
    covid["month"] = covid["date"].dt.to_period("M").astype(str)
    monthly = covid.groupby(["country", "month"], as_index=False).agg(
        reported_new_cases=("new_cases", lambda s: s.sum(min_count=1)),
        observed_days=("new_cases", "count"),
        source_rows=("date", "size"),
    ).sort_values(["country", "month"]).reset_index(drop=True)

    orders = read_json("orders_json/orders.json")
    customers = read_json("orders_json/customers.json")
    require({"order_id", "customer_id", "product", "quantity",
             "total_amount"}.issubset(orders.columns), "Orders schema")
    require({"customer_id", "customer_name", "city"}.issubset(
            customers.columns), "Customers schema")
    orders = orders.drop_duplicates().copy()
    customers = customers.drop_duplicates().copy()
    for col in ["order_id", "customer_id", "quantity"]:
        positive_int(orders, col)
    positive_int(customers, "customer_id")
    require(not orders["order_id"].duplicated().any(),
            "Conflicting order IDs")
    require(not customers["customer_id"].duplicated().any(),
            "Conflicting customer IDs")
    orders["total_amount"] = pd.to_numeric(
        orders["total_amount"], errors="raise")
    require(orders["total_amount"].notna().all()
            and orders["total_amount"].ge(0).all()
            and orders["total_amount"].lt(float("inf")).all(),
            "Invalid order amounts")
    for frame, cols in [(orders, ["product"]),
                         (customers, ["customer_name", "city"])]:
        for col in cols:
            require(frame[col].notna().all(), f"Missing {col}")
            frame[col] = frame[col].astype("string").str.strip()
            require(frame[col].ne("").all(), f"Blank {col}")
    silver = orders.merge(customers, on="customer_id", how="left",
                          validate="many_to_one", indicator=True)
    require(silver["_merge"].eq("both").all(), "Unknown customer ID")
    silver = silver.drop(columns="_merge").sort_values(
        "order_id").reset_index(drop=True)
    sales = silver.groupby("city", as_index=False).agg(
        order_count=("order_id", "nunique"),
        total_quantity=("quantity", "sum"),
        total_sales=("total_amount", "sum"),
    ).sort_values("city").reset_index(drop=True)
    require(sales["order_count"].sum() == len(silver),
            "Order count does not reconcile")
    require(abs(sales["total_sales"].sum()
                - silver["total_amount"].sum()) < 0.005,
            "Sales totals do not reconcile")
    return silver, monthly, sales

def main():
    for path in ["covid/owid-covid-data.csv",
                 "orders_json/orders.json", "orders_json/customers.json"]:
        client = service.get_file_client("raw", path)
        require(client.get_file_properties().size > 0,
                f"Empty Raw file: {path}")
        print(f"PASS | raw/{path}")
    silver, monthly, sales = build_outputs()
    outputs = [
        ("staging", "orders/orders_clean.parquet", silver),
        ("curated", "covid/uk/monthly_cases.parquet", monthly),
        ("curated", "orders/sales_by_city.parquet", sales),
    ]
    for zone, path, frame in outputs:
        write_parquet(zone, path, frame)
    print(sales.to_string(index=False))
    print(monthly.tail(5).to_string(index=False))
    print("PASS: Day 38 complete zone validation succeeded")

if __name__ == "__main__":
    main()
