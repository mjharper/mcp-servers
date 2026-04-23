# slack-mcp-server

A lightweight [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes Slack message sending via the Slack Web API as tools. Designed for use with VS Code in agent mode and Claude Code.

## Tools

| Tool | Description |
|---|---|
| `send_message` | Send a plain text message to a Slack channel or user |
| `send_formatted_message` | Send a [Block Kit](https://api.slack.com/block-kit) formatted message to a Slack channel or user |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- A Slack bot token with `chat:write` scope

## Installation

```bash
# Install from the project directory
cd slack-mcp-server
uv pip install -e .
```

Or install directly without cloning using `uvx`:

```bash
uvx --from . slack-mcp-server
```

## Configuration

The server reads one environment variable at startup:

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | A Slack bot token with `chat:write` scope (starts with `xoxb-`) |

## Running

```bash
SLACK_BOT_TOKEN=xoxb-xxxx \
slack-mcp-server
```

The server communicates over **stdio** only.

## VS Code integration

### `.vscode/mcp.json`

```json
{
  "servers": {
    "slack": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/slack-mcp-server",
        "run",
        "slack-mcp-server"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "${input:slackBotToken}"
      }
    }
  },
  "inputs": [
    {
      "id": "slackBotToken",
      "type": "promptString",
      "description": "Slack Bot Token (xoxb-...)",
      "password": true
    }
  ]
}
```

The `${input:slackBotToken}` placeholder causes VS Code to prompt for the token once per session so it is never stored on disk.
