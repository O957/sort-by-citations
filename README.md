# Citation Search Web App

A simple, lightweight Streamlit application to find the most cited academic papers by keyword or author using the OpenAlex API.

## Features

- **Dual search modes** - Search by keyword or author name
- **Simple interface** - Clean Streamlit design with sidebar filters
- **Powerful search** - Search 250M+ papers from OpenAlex
- **Author disambiguation** - Shows author affiliation and metrics to help identify the correct person
- **Advanced filters** - Filter by year range, citation count, and open access status
- **Download results** - Export as TXT (titles or full data) or CSV with static filenames
- **HTML rendering** - Properly displays italics and superscripts in paper titles
- **Polite pool access** - Add your email for better performance
- **No API key needed** - OpenAlex is free and open
- **Local assets** - All fonts and content stored locally for faster loading

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
   - Number of results (5-100)
   - Min/Max year
   - Minimum citations
   - Open access only
3. **Choose search mode**: Keyword or Author
4. **Enter your search**:
   - Keyword: e.g., "machine learning", "CRISPR", "climate change"
   - Author: e.g., "Albert Einstein", "Marie Curie"
5. **Click "Search"**
6. **Browse results** sorted by citation count
   - For author searches, view author info (affiliation, total works, citations, ORCID)
7. **Download results** as TXT or CSV

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
├── assets/
│   ├── content/        # markdown content files
│   │   ├── about_openalex.md
│   │   ├── api_comparison.md
│   │   ├── repository_info.md
│   │   └── search_tips.md
│   └── fonts/          # local font files
│       └── BebasNeue-Regular.ttf
├── pyproject.toml      # project dependencies (uv)
├── requirements.txt    # dependencies for streamlit cloud
├── .streamlit/
│   └── config.toml    # streamlit theme configuration
└── README.md           # this file
```

## API Usage

**NOTE:** This application uses the OpenAlex polite pool system when an email is provided. The app is designed to be respectful to the OpenAlex API by:
- Using the polite pool for better, more consistent performance
- Sending your email to OpenAlex so they can contact you if needed
- Following OpenAlex's rate limiting guidelines

## Acknowledgments

- **OpenAlex** - Free, open API for scholarly data
- **pyalex** - Python wrapper for OpenAlex API
- **Streamlit** - Web framework for data applications

## Contributing

Contributions are welcome! Here's how you can help:

- **Report issues** - Found a bug or have a feature request? [Open an issue](https://github.com/O957/sort-by-citations/issues)
- **Submit pull requests** - Have a fix or improvement? [Create a pull request](https://github.com/O957/sort-by-citations/pulls)
- **Join discussions** - Share ideas and provide feedback in [Discussions](https://github.com/O957/sort-by-citations/discussions)
- **Contact** - Email me at: [my github username]+[@]+[pro]+[ton]+[.]+[me]

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
