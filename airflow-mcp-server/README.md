# airflow-mcp-server

A lightweight [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes a small subset of the Apache Airflow REST API v2 as tools. Designed for use with VS Code in agent mode and Claude Code.

## Tools

| Tool | Description |
|---|---|
| `list_dags` | List / search DAGs, optionally filtering by ID pattern or active status |
| `get_dag` | Get details for a specific DAG, including enabled/paused state |
| `get_last_dag_run` | Get the status of the most recent run for a DAG |
| `get_dag_run_errors` | Get error details and task logs for the most recent failed DAG run |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- [gcloud CLI](https://cloud.google.com/sdk/gcloud) authenticated with an account that has access to your Airflow instance

## Authentication

The server uses `gcloud auth print-identity-token` to obtain a Google-signed ID token (JWT) at startup and sends it as a Bearer token. This is required for Cloud Composer, whose Airflow webserver is fronted by IAP (Identity-Aware Proxy). IAP rejects OAuth access tokens and basic auth with 401 — it only accepts ID tokens.

Make sure you are authenticated before starting the server:

```bash
gcloud auth login
# or for workload identity / CI environments:
gcloud auth application-default login
```

The token is fetched once at startup and lasts approximately one hour. Restart the server if it expires during a long session.

## Installation

```bash
cd airflow-mcp-server
uv pip install -e .
```

## Configuration

The server reads one environment variable at startup:

| Variable | Description |
|---|---|
| `AIRFLOW_API_URL` | Base URL of the Airflow REST API. Use `/api/v1` for Airflow 2.x (including Cloud Composer 2, e.g. Airflow 2.10.x), `/api/v2` for Airflow 3.x. |

## Running

```bash
AIRFLOW_API_URL=https://airflow.example.com/api/v1 airflow-mcp-server
```

The server communicates over **stdio** only.

## VS Code integration

### `.vscode/mcp.json`

```json
{
  "servers": {
    "airflow": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/airflow-mcp-server",
        "run",
        "airflow-mcp-server"
      ],
      "env": {
        "AIRFLOW_API_URL": "https://airflow.example.com/api/v1"
      }
    }
  }
}
```
