from io import BytesIO
import os
import pandas as pd
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.filedatalake import DataLakeServiceClient

ACCOUNT = "stderoadmapdvrr26"

s = DataLakeServiceClient(
    account_url=f"https://{ACCOUNT}.dfs.core.windows.net",
    credential=AzureNamedKeyCredential(ACCOUNT, os.environ["STORAGE_KEY"]),
)

def read(zone, path):
    f = s.get_file_client(zone, path)
    assert f.get_file_properties().size > 0, path
    return pd.read_parquet(BytesIO(f.download_file().readall()))

a = read("staging", "orders/orders_clean.parquet")
b = read("curated", "orders/sales_by_city.parquet")
c = read("curated", "covid/uk/monthly_cases.parquet")
u = read("staging", "covid/uk/owid-covid-uk.parquet")

assert len(a) == 2 and a.order_id.is_unique
assert a.quantity.sum() == 3
assert abs(a.total_amount.sum() - 940) < 0.005

expected = {"London": 850.0, "Manchester": 90.0}
assert b.set_index("city").total_sales.to_dict() == expected
assert b.order_count.sum() == len(a)
assert b.total_quantity.sum() == a.quantity.sum()

assert not c.empty and not c.duplicated(["country", "month"]).any()
assert c.country.eq("United Kingdom").all()

u["date"] = pd.to_datetime(u["date"], errors="raise")
u["new_cases"] = pd.to_numeric(u["new_cases"], errors="raise")
assert u["date"].notna().all()
assert not u.duplicated(["country", "date"]).any()

u["month"] = u["date"].dt.to_period("M").astype(str)
expected_c = u.groupby(["country", "month"]).new_cases.sum(min_count=1)
actual_c = c.set_index(["country", "month"]).reported_new_cases

pd.testing.assert_series_equal(
    expected_c.sort_index(),
    actual_c.sort_index(),
    check_names=False,
    check_dtype=False,
)

print(b.to_string(index=False))
print("COVID months:", len(c))
print("PASS: Independent Day 38 read back and reconciliation")
