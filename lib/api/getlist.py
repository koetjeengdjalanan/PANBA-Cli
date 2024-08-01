from typing import Any
import requests

from pydantic import BaseModel


class ElementOfTenant(BaseModel):
    bearerToken: str
    headers: dict = {
        "Accept": "application/json",
        "User-Agent": "NTTIndonesia-PANBA/0.2.0",
    }
    uri: str = "/sdwan/v3.1/api/elements"
    data: dict | None = None

    def model_post_init(self, *args, **kwargs):
        from lib.api import base_url

        self.headers.update({"Authorization": f"Bearer {self.bearerToken}"})
        res = requests.get(url=f"{base_url}{self.uri}", headers=self.headers)
        res.raise_for_status()
        self.data = res.json()


class InterfaceOfTenant(BaseModel):
    bearerToken: str
    siteId: str
    elementId: str
    headers: dict = {
        "Accept": "application/json",
        "User-Agent": "NTTIndonesia-PANBA/0.2.0",
    }
    uri: str = "/sdwan/v4.18/api/sites"
    data: dict | None = None

    def model_post_init(self, __context: Any) -> None:
        from lib.api import base_url

        self.headers.update({"Authorization": f"Bearer {self.bearerToken}"})
        res = requests.get(
            url=f"{base_url}{self.uri}/{self.siteId}/elements/{self.elementId}/interfaces",
            headers=self.headers,
        )
        res.raise_for_status()
        self.data = res.json()
