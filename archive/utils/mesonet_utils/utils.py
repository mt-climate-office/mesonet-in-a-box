import httpx
from typing import Optional


def check_airtable_token(token: Optional[str]) -> bool:
    if token is None:
        return False

    response = httpx.get(
        url="https://api.airtable.com/v0/meta/bases",
        headers={"Authorization": f"Bearer {token}"},
    )

    return response.status_code == 200
