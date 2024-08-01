import requests

from rich.console import Console
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth
from datetime import datetime as dt, timedelta as delta


class ApiAuth(BaseModel):
    userName: str
    secret: str
    tsgId: int | str
    url: str = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
    bearerToken: str | None = None
    expire: dt | None = None
    verbose: bool = False

    def model_post_init(self, *args, **kwargs):
        console = Console()
        res = requests.post(
            url=self.url,
            auth=HTTPBasicAuth(username=self.userName, password=self.secret),
            data={
                "grant_type": "client_credentials",
                "scope": f"tsg_id:{self.tsgId}",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "NTTIndonesia-PANBA-Cli/0.0.1",
            },
        )
        (
            console.log("Generating Token", res.status_code, sep="\n")
            if self.verbose
            else None
        )
        res.raise_for_status()
        self.bearerToken = str(res.json()["access_token"])
        self.expire = dt.now() + delta(seconds=res.json()["expires_in"])
        (
            console.log(
                "Token Expired: ", dt.strftime(self.expire, format="%d/%m/%Y, %H:%M:%S")
            )
            if self.verbose
            else None
        )
        self.__getProfile()

    def __getProfile(self) -> None:
        from lib.api import base_url

        res = requests.get(
            url=f"{base_url}/sdwan/v2.1/api/profile",
            headers={
                "Accept": "application/json",
                "User-Agent": "NTTIndonesia-PANBA/0.2.0",
                "Authorization": f"Bearer {self.bearerToken}",
            },
        )
        console = Console()
        (
            console.log("Getting Profiles", res.status_code, sep="\n")
            if self.verbose
            else None
        )
        res.raise_for_status()
        # profile = res.json()
