# multimodal-rag-agent
# Research MCP Server

## Step 0 — Prerequisites

```bash
mkdir research-mcp-server
cd research-mcp-server
python -m venv venv
venv\Scripts\activate      # on Mac/Linux: source venv/bin/activate
pip install mcp sentence-transformers chromadb pypdf --break-system-packages
```

## Step 1 — Prepare your data

```bash
mkdir papers   # drop your thesis + paper PDFs in here
python prepare_data.py
```

## Step 2 — Build the searchable vector store

```bash
python build_index.py
```

## Step 3 — Write the MCP server itself

See `server.py`.

`mcp` v2.x renamed `FastMCP` to `MCPServer`. If you're on mcp 2.x, import it like this:

```python
from mcp.server.mcpserver import MCPServer
server = MCPServer("research-papers")
```

not `from mcp.server.fastmcp import FastMCP` — that's the old v1 way and throws `ModuleNotFoundError` on v2.

Don't load the embedding model or chroma client at the top of the file. Load them lazily, inside the tool functions, the first time they're actually used. Claude Desktop expects a reply within ~60s of connecting, and loading torch + sentence-transformers eagerly can take longer than that on a slow/cold machine — the server just sits there and gets marked "Failed" even though nothing's actually wrong with it.

Use absolute paths for the `chroma_store` folder, anchored to the script's own location:

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_store")
```

A relative path like `"./chroma_store"` works fine when you run it from your terminal but breaks when Claude Desktop launches it from somewhere else.

## Step 4 — Test it locally before connecting anything

```bash
pip install "mcp[cli]" --break-system-packages
mcp dev server.py
```

Open the Inspector link it gives you and try `list_papers` / `search_papers` there first, before touching Claude Desktop.

## Step 5 — Connect it to Claude Desktop

Open Claude Desktop → **Settings → Developer → Edit config**. This is the config file Desktop actually reads — don't go hunting for `%APPDATA%` yourself, just use this button.

Add:

```json
{
  "mcpServers": {
    "research-papers": {
      "command": "C:/absolute/path/to/research-mcp-server/venv/Scripts/python.exe",
      "args": ["-u", "C:/absolute/path/to/research-mcp-server/server.py"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

Use forward slashes even on Windows. Point `command` at the `python.exe` inside your venv, not just `python3`.

Fully quit Claude Desktop from the tray icon (not just close the window), reopen it, then check Settings → Developer again — `research-papers` should say **Running**. If it says **Failed**, click **View logs**.

Then in a new chat ask: *"What papers are available in my research server?"* — Claude should call `list_papers` and answer from the real data.

## Step 6 — Ask it real research questions

- "Does any of my papers use skeletal data, and which one specifically?"
- "Summarize the difference in accuracy reported between paper 2 and paper 4."
- "Which of my papers would be most relevant to someone working on RGB-only gesture recognition?"

Watch for Claude calling `search_papers` before it answers — that's how you know it's actually reading your papers and not just guessing.

## Common problems and fixes

**`ModuleNotFoundError: No module named 'mcp'`**
Venv isn't activated. Run `venv\Scripts\activate` first.

**`ModuleNotFoundError: No module named 'mcp.server.fastmcp'`**
You're on mcp 2.x. Use `MCPServer` instead of `FastMCP` (see Step 3).

**Works in `mcp dev` / the Inspector but fails in Claude Desktop**
Usually a working-directory or env var problem. The Inspector runs your script from inside the project folder, so relative paths and anything you `set` manually in your terminal still apply. Desktop runs it from somewhere else entirely, with none of that. Fix: absolute paths anchored to the script's own folder, and set env vars in the script itself (`os.environ.setdefault(...)`) or in the config's `"env"` block, not just in your terminal session.

**Status shows "Failed" in Settings → Developer, logs don't show an obvious crash**
Look at the timestamps in the logs. If you see `initialize` sent by the client, then nothing, then `notifications/cancelled` about 60 seconds later — that's a timeout, not a crash. Your script accepted the connection but took too long to finish starting up. Fix: lazy-load the model and chroma client instead of loading them at import time (see Step 3).

**"Add custom connector" dialog wants an HTTPS URL**
That's for remote MCP servers, not local ones. A local server like this goes in `claude_desktop_config.json` via Settings → Developer → Edit config, not that dialog.

**`search_papers` returns nothing relevant**
Check `chunks.json` first — if the PDF text extraction looked garbled in Step 1, fix that before touching the server code.

**Chunks cut off mid-sentence**
Normal with fixed-size chunking. If it actually hurts answer quality, switch to splitting on paragraph breaks before falling back to a hard character cut.

**`list_papers` returns weird IDs like `1`, `59`, `08818760 s-t`**
That's just your PDF filenames. Rename the files if you want cleaner names, or pull the real title out of each PDF in `prepare_data.py` instead of using the filename.
