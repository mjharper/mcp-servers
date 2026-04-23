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

## Installation

```bash
# Install from the project directory
cd airflow-mcp-server
uv pip install -e .
```

Or install directly without cloning using `uvx`:

```bash
uvx --from . airflow-mcp-server
```

## Configuration

The server reads three environment variables at startup:

| Variable | Description |
|---|---|
| `AIRFLOW_API_URL` | Base URL of the Airflow REST API, e.g. `https://airflow.example.com/api/v1` |
| `AIRFLOW_USERNAME` | Airflow username |
| `AIRFLOW_PASSWORD` | Airflow password |

## Running

```bash
AIRFLOW_API_URL=https://airflow.example.com/api/v1 \
AIRFLOW_USERNAME=admin \
AIRFLOW_PASSWORD=secret \
airflow-mcp-server
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
        "AIRFLOW_API_URL": "https://airflow.example.com/api/v1",
        "AIRFLOW_USERNAME": "${input:airflowUsername}",
        "AIRFLOW_PASSWORD": "${input:airflowPassword}"
      }
    }
  },
  "inputs": [
    {
      "id": "airflowUsername",
      "type": "promptString",
      "description": "Airflow username"
    },
    {
      "id": "airflowPassword",
      "type": "promptString",
      "description": "Airflow password",
      "password": true
    }
  ]
}
```

The `${input:...}` placeholders cause VS Code to prompt for credentials once per session so they are never stored on disk.
