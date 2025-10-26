# Citation Search Web App

A simple, lightweight Streamlit application to find the most cited academic papers by keyword using the OpenAlex API.

## Features

- **Simple interface** - Clean Streamlit design with sidebar filters
- **Powerful search** - Search 250M+ papers from OpenAlex
- **Advanced filters** - Filter by year range, citation count, and open access status
- **Download results** - Export as TXT (titles or full data) or CSV
- **Polite pool access** - Add your email for better performance
- **No API key needed** - OpenAlex is free and open

## Quick Start

### Installation

```bash
# install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# install dependencies
uv sync
```

### Running Locally

```bash
# run the streamlit app
uv run streamlit run streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Usage

1. **Enter your email** (optional) in the sidebar for polite pool access
2. **Set filters** in the sidebar:
   - Number of results (10-100)
   - Min/Max year
   - Minimum citations
   - Open access only
3. **Enter a keyword** (e.g., "machine learning", "CRISPR", "climate change")
4. **Click "Search"**
5. **Browse results** sorted by citation count
6. **Download results** as TXT or CSV

## Technology Stack

- **Framework**: Streamlit
- **API**: OpenAlex via pyalex library
- **Data**: polars for data handling and CSV export
- **Package manager**: uv

## Deployment to Streamlit Cloud (Free!)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "add streamlit app"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `O957/sort-by-citations`
5. Set main file path: `streamlit_app.py`
6. Click "Deploy"

**That's it!** Your app will be live at `https://[your-app-name].streamlit.app` in ~2 minutes.

### Optional: Set Environment Variable

In Streamlit Cloud settings, add:
- **Key**: `OPENALEX_EMAIL`
- **Value**: `your@email.com`

This provides a default email for users who don't provide their own.

## Alternative Deployment Options

### Railway
```bash
# install railway CLI
curl -fsSL https://railway.app/install.sh | sh

# login and deploy
railway login
railway up
```

### Render
Create a `render.yaml`:
```yaml
services:
  - type: web
    name: sort-by-citations
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0"
```

## File Structure

```
sort-by-citations/
├── streamlit_app.py    # main streamlit application
├── app.py              # archived flask version
├── templates/          # archived flask templates
├── pyproject.toml      # project dependencies (uv)
├── requirements.txt    # dependencies for streamlit cloud
├── .streamlit/
│   └── config.toml    # streamlit theme configuration
└── README.md           # this file
```

## Archived Flask Version

The original Flask version is archived in this repository:
- `app.py` - Flask backend
- `templates/index.html` - HTML/JS frontend

To run the Flask version:
```bash
uv sync --extra flask
uv run python3 app.py
```

## Acknowledgments

- **OpenAlex** - Free, open API for scholarly data
- **pyalex** - Python wrapper for OpenAlex API
- **clipboard2markdown** - Inspiration for simple, clean design

## License

Copyright 2025 O957 (Pseudonym)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
