# dbt-mcp-server

A lightweight [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes a small subset of the dbt Cloud REST API as tools. Designed for use with VS Code in agent mode and Claude Code.

## Tools

| Tool | Description |
|---|---|
| `find_project_by_name` | Find a dbt Cloud project by its exact name |
| `list_environment_variables` | List environment variable names for a dbt Cloud project |
| `list_jobs` | List dbt Cloud jobs, optionally filtered by project |
| `get_job_run_errors` | Get step-level logs for the most recent failed run of a job |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management

## Installation

```bash
# Install from the project directory
cd dbt-mcp-server
uv pip install -e .
```

Or install directly without cloning using `uvx`:

```bash
uvx --from . dbt-mcp-server
```

## Configuration

The server reads the following environment variables at startup:

| Variable | Required | Description |
|---|---|---|
| `DBT_CLOUD_API_TOKEN` | Yes | dbt Cloud API token |
| `DBT_CLOUD_ACCOUNT_ID` | Yes | Numeric dbt Cloud account ID |
| `DBT_CLOUD_ADMIN_API_URL` | No | dbt Cloud admin API v3 base URL (default: `https://cloud.getdbt.com/api/v3`) |
| `DBT_CLOUD_ADMIN_V2_URL` | No | dbt Cloud admin API v2 base URL (default: `https://cloud.getdbt.com/api/v2`) |

## Running

```bash
DBT_CLOUD_API_TOKEN=dbtc_xxxx \
DBT_CLOUD_ACCOUNT_ID=12345 \
dbt-mcp-server
```

The server communicates over **stdio** only.

## VS Code integration

### `.vscode/mcp.json`

```json
{
  "servers": {
    "dbt": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/dbt-mcp-server",
        "run",
        "dbt-mcp-server"
      ],
      "env": {
        "DBT_CLOUD_API_TOKEN": "${input:dbtToken}",
        "DBT_CLOUD_ACCOUNT_ID": "${input:dbtAccountId}",
        "DBT_CLOUD_ADMIN_API_URL": "https://cloud.getdbt.com/api/v3",
        "DBT_CLOUD_ADMIN_V2_URL": "https://cloud.getdbt.com/api/v2"
      }
    }
  },
  "inputs": [
    {
      "id": "dbtToken",
      "type": "promptString",
      "description": "dbt Cloud API Token",
      "password": true
    },
    {
      "id": "dbtAccountId",
      "type": "promptString",
      "description": "dbt Cloud Account ID"
    }
  ]
}
```

The `${input:dbtToken}` placeholder causes VS Code to prompt for the token once per session so it is never stored on disk.
