import asyncio
import os
import shutil
from typing import Any

import httpx

_GCLOUD_SEARCH_PATH = ":".join([
    os.path.expanduser("~/google-cloud-sdk/bin"),
    "/usr/local/bin",
    "/usr/bin",
    "/bin",
    "/opt/homebrew/bin",
    "/snap/bin",
])


def _find_gcloud() -> str:
    path = shutil.which("gcloud", path=_GCLOUD_SEARCH_PATH)
    if not path:
        raise RuntimeError(
            "gcloud not found. Ensure the Google Cloud SDK is installed. "
            f"Searched: {_GCLOUD_SEARCH_PATH}"
        )
    return path


class AirflowError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"Airflow API error {status_code}: {message}")


async def _gcloud_login(gcloud: str, account: str | None) -> None:
    """Trigger browser-based gcloud auth login and wait for it to complete."""
    cmd = [gcloud, "auth", "login", "--no-launch-browser", "--brief"]
    if account:
        cmd += ["--account", account]
    # Re-run without --no-launch-browser so the browser opens automatically
    cmd = [gcloud, "auth", "login", "--brief"]
    if account:
        cmd += ["--account", account]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"gcloud auth login failed: {stderr.decode().strip()}")


async def _get_gcloud_token() -> str:
    gcloud = _find_gcloud()
    account = os.environ.get("AIRFLOW_GCLOUD_ACCOUNT")
    cmd = [gcloud, "auth", "print-access-token"]
    if account:
        cmd += ["--account", account]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err = stderr.decode().strip()
        if "invalid_grant" in err or "Bad Request" in err or "does not have any valid credentials" in err:
            # Credentials expired — trigger browser login and retry once
            await _gcloud_login(gcloud, account)
            proc2 = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc2.communicate()
            if proc2.returncode != 0:
                raise RuntimeError(f"gcloud auth print-access-token failed after re-login: {stderr.decode().strip()}")
        else:
            raise RuntimeError(f"gcloud auth print-access-token failed: {err}")
    return stdout.decode().strip()


class AirflowClient:
    def __init__(self) -> None:
        base_url = os.environ.get("AIRFLOW_API_URL", "").rstrip("/")
        if not base_url:
            raise RuntimeError("AIRFLOW_API_URL environment variable is not set")

        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0,
            follow_redirects=True,
        )

    async def authenticate(self) -> None:
        token = await _get_gcloud_token()
        self._client.headers["Authorization"] = f"Bearer {token}"

    async def _do_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = await self._client.request(method, path, **kwargs)
        if response.status_code == 401:
            await self.authenticate()
            response = await self._client.request(method, path, **kwargs)
        return response

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = await self._do_request(method, path, **kwargs)
        if not response.is_success:
            raise AirflowError(response.status_code, response.text)
        return response.json()

    async def list_dags(
        self,
        dag_id_pattern: str | None = None,
        only_active: bool = False,
        limit: int = 20,
    ) -> Any:
        params: dict[str, Any] = {"limit": limit}
        if dag_id_pattern:
            params["dag_id_pattern"] = dag_id_pattern
        if only_active:
            params["only_active"] = True
        return await self._request("GET", "/dags", params=params)

    async def get_dag(self, dag_id: str) -> Any:
        return await self._request("GET", f"/dags/{dag_id}")

    async def get_last_dag_run(self, dag_id: str) -> dict[str, Any] | None:
        data = await self._request(
            "GET",
            f"/dags/{dag_id}/dagRuns",
            params={"limit": 1, "order_by": "-start_date"},
        )
        runs: list[Any] = data.get("dag_runs", [])
        return runs[0] if runs else None

    async def get_failed_task_instances(self, dag_id: str, dag_run_id: str) -> list[Any]:
        data = await self._request(
            "GET",
            f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
            params={"state": "failed"},
        )
        return data.get("task_instances", [])

    async def get_task_logs(self, dag_id: str, dag_run_id: str, task_id: str, try_number: int) -> str:
        response = await self._do_request(
            "GET",
            f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}",
        )
        if not response.is_success:
            raise AirflowError(response.status_code, response.text)
        return response.text

    async def aclose(self) -> None:
        await self._client.aclose()
