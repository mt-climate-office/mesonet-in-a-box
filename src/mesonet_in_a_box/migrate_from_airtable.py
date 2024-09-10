import polars as pl


def get_airtable_records(
    base: str, table: str, columns: str | None = None
) -> pl.DataFrame:
    if columns is None:
        columns = []
    url = f"https://api.airtable.com/v0/{base}/{table}"
    params = {
        "fields[]": columns,
    }
    header = {"Authorization": "Bearer TOKEN"}

    return url, params, header
