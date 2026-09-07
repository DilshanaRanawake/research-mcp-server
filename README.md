# multimodal-rag-agent

# Research MCP Server

## Step 0 — Prerequisites

```bash
mkdir research-mcp-server
cd research-mcp-server
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install mcp sentence-transformers chromadb pypdf --break-system-packages
```

## Step 1 — Prepare your data

```bash
mkdir papers   # drop your thesis + 5 paper PDFs in here
python3 prepare_data.py
```

## Step 2 — Build the searchable vector store

```bash
python3 build_index.py
```

## Step 3 — Write the MCP server itself

## Step 4 — Test it locally before connecting anything

```bash
pip install "mcp[cli]" --break-system-packages
mcp dev server.py
```

## Step 5 — Connect it to Claude Desktop

Find (or create) Claude Desktop's config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add your server to it:

```json
{
  "mcpServers": {
    "research-papers": {
      "command": "python3",
      "args": ["/absolute/path/to/research-mcp-server/server.py"]
    }
  }
}
```

Restart Claude Desktop completely. You should see a small tool/plug icon indicating research-papers is connected.

Check it worked: in a new Claude Desktop chat, ask something like "What papers are available in my research server?" — Claude should call list_papers and answer from the real result, not from general knowledge.

## Step 6 — Ask it real research questions

Now the actual demo. Try questions like:

- "Does any of my papers use skeletal data, and which one specifically?"
- "Summarize the difference in accuracy reported between paper 2 and paper 4."
- "Which of my papers would be most relevant to someone working on RGB-only gesture recognition?"

Watch whether Claude calls search_papers (visible in the Claude Desktop UI as a tool call) before answering — that's the proof it's grounding the answer in your real data, not guessing.

## Common problems and fixes

- **ModuleNotFoundError: No module named 'mcp'** — make sure your virtual environment is activated (`source venv/bin/activate`) before running any script.

- **Claude Desktop doesn't show the tool icon** — double check the path in `claude_desktop_config.json` is absolute, not relative, and that you fully quit and reopened Claude Desktop (not just closed the window).

- **search_papers returns nothing relevant** — check `chunks.json` first; if the text extraction looked garbled in Step 1, fix that before touching the server code.

- **Chunks cut off mid-sentence and hurt answer quality** — this is expected with fixed-size chunking; if it's bad enough to matter, switch to splitting on paragraph breaks before falling back to a hard character cut.
