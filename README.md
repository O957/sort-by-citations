# Citation Search

_Streamlit application which uses the OpenAlex API (via pyalex) to find the top N academic resources by citation count for researcher or keyword searches._

> [!IMPORTANT]
>
> The application is live at: <https://sort-by-citations.streamlit.app/>. You may need to "wake up" the application, as `streamlit` cloud will shut down the application during periods of inactivity.

## Features

- **Keyword Search**: Find top cited papers by research topic or keyword.
- **Author Search**: Discover an author's most cited works.
- **Advanced Filtering**: Filter by publication year, minimum citations, and open access status.
- **Multiple Export Formats**: Download results as TXT or CSV files.
- **Rate Limit Management**: Optional email input for OpenAlex polite pool access (faster response times).
- **Rich Metadata**: View author information, publication year, source, DOI, and open access status.

## Installation

This project uses `uv` for dependency management. Installation instructions for `uv` can be found here: <https://github.com/astral-sh/uv>.

To install `sort-by-citations`:

```bash
# clone the repository
git clone https://github.com/O957/sort-by-citations.git
cd sort-by-citations

# install dependencies with uv
uv sync
```

## Usage

Run the application locally:

```bash
uv run streamlit run streamlit_app.py
```

or just

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501` (paste this in your browser).

### API Access

The application uses the [OpenAlex API](https://openalex.org). Providing your email (optional) grants access to the "polite pool" with better rate limits and response times. Your email is sent directly to OpenAlex and not stored by this application.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

```
Copyright O957 (Pseudonym)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
