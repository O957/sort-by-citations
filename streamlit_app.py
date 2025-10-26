"""
Streamlit web application to find top cited papers using
OpenAlex. This application provides an interface for
searching the most cited academic papers by keyword or
author using the OpenAlex API (via pyalex).
"""

import base64
import os
from datetime import datetime
from pathlib import Path

import polars as pl
import requests
import streamlit as st
from pyalex import Authors, Works, config


def load_markdown_content(filename: str) -> str:
    """
    Load markdown content from assets/content directory.

    Parameters
    ----------
    filename : str
        Name of the markdown file to load.

    Returns
    -------
    str
        Content of the markdown file, or empty string if file not found.
    """
    content_path = Path(__file__).parent / "assets" / "content" / filename
    if content_path.exists():
        return content_path.read_text()
    return ""


def load_font_base64(font_path: str) -> str:
    """
    Load font file and encode as base64 for CSS embedding.

    Parameters
    ----------
    font_path : str
        Path to the font file.

    Returns
    -------
    str
        Base64 encoded font data.
    """

    font_file = Path(__file__).parent / font_path
    if font_file.exists():
        return base64.b64encode(font_file.read_bytes()).decode()
    return ""


# page configuration
st.set_page_config(
    page_title="Citation Search",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# initialize session state
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "rate_limit_info" not in st.session_state:
    st.session_state.rate_limit_info = None
if "author_info" not in st.session_state:
    st.session_state.author_info = None
if "search_type" not in st.session_state:
    st.session_state.search_type = "keyword"


def get_openalex_rate_limit_info(user_email: str | None = None) -> dict:
    """
    Make a test request to OpenAlex to get rate limit headers.

    Parameters
    ----------
    user_email : str | None
        User email for polite pool.

    Returns
    -------
    dict
        Rate limit information from OpenAlex headers.
    """
    email = user_email or os.environ.get(
        "OPENALEX_EMAIL", "research@example.com"
    )

    url = "https://api.openalex.org/works"
    params = {"per-page": 1, "mailto": email}

    try:
        response = requests.get(url, params=params, timeout=5)
        headers = response.headers

        limit = headers.get(
            "ratelimit-limit", headers.get("x-ratelimit-limit", "unknown")
        )
        remaining = headers.get(
            "ratelimit-remaining",
            headers.get("x-ratelimit-remaining", "unknown"),
        )

        return {
            "rate_limit_limit": limit,
            "rate_limit_remaining": remaining,
            "email_used": email,
            "has_email": bool(user_email),
        }
    except Exception as e:
        return {
            "error": str(e),
            "email_used": email,
            "has_email": bool(user_email),
        }


def extract_paper_info(work: dict) -> dict:
    """
    Extract relevant fields from a work object.

    Parameters
    ----------
    work : dict
        Work object from OpenAlex API.

    Returns
    -------
    dict
        Extracted paper information.
    """
    authors = [
        authorship.get("author", {}).get("display_name", "Unknown")
        for authorship in work.get("authorships", [])[:5]
        if authorship.get("author")
    ]

    # handle None values for nested dicts
    open_access_data = work.get("open_access") or {}
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}

    return {
        "title": work.get("title", "No title"),
        "authors": ", ".join(authors) if authors else "Unknown",
        "year": work.get("publication_year"),
        "citations": work.get("cited_by_count", 0),
        "doi": work.get("doi"),
        "url": work.get("doi") if work.get("doi") else None,
        "open_access": open_access_data.get("is_oa", False),
        "source": source.get("display_name", "Unknown"),
    }


def search_papers(
    keyword: str,
    limit: int = 25,
    min_year: int | None = None,
    max_year: int | None = None,
    min_citations: int | None = None,
    open_access_only: bool = False,
    user_email: str | None = None,
) -> list[dict]:
    """
    Search OpenAlex for top cited papers by keyword.

    Parameters
    ----------
    keyword : str
        Search keyword.
    limit : int
        Number of results to return.
    min_year : int | None
        Minimum publication year.
    max_year : int | None
        Maximum publication year.
    min_citations : int | None
        Minimum citation count.
    open_access_only : bool
        Only return open access papers.
    user_email : str | None
        User email for polite pool access.

    Returns
    -------
    list[dict]
        List of paper dicts.
    """
    # set email for this request
    if user_email:
        config.email = user_email
    else:
        config.email = os.environ.get("OPENALEX_EMAIL", "research@example.com")

    # build query
    query = Works().search(keyword)

    # apply filters
    if min_year:
        query = query.filter(from_publication_date=f"{min_year}-01-01")
    if max_year:
        query = query.filter(to_publication_date=f"{max_year}-12-31")
    if open_access_only:
        query = query.filter(is_oa=True)

    # sort by citations and get results
    fetch_limit = limit * 3 if min_citations else limit
    results = query.sort(cited_by_count="desc").get(
        per_page=min(fetch_limit, 200)
    )

    # extract information from all works
    papers = [extract_paper_info(work) for work in results]

    # apply client-side citation filter if needed
    if min_citations:
        papers = [p for p in papers if p["citations"] >= min_citations]

    # return only requested number
    return papers[:limit]


def search_papers_by_author(
    author_name: str,
    limit: int = 25,
    min_year: int | None = None,
    max_year: int | None = None,
    min_citations: int | None = None,
    open_access_only: bool = False,
    user_email: str | None = None,
) -> tuple[list[dict], dict | None]:
    """
    Search OpenAlex for top cited papers by author name.

    Parameters
    ----------
    author_name : str
        Author name to search for.
    limit : int
        Number of results to return.
    min_year : int | None
        Minimum publication year.
    max_year : int | None
        Maximum publication year.
    min_citations : int | None
        Minimum citation count.
    open_access_only : bool
        Only return open access papers.
    user_email : str | None
        User email for polite pool access.

    Returns
    -------
    tuple[list[dict], dict | None]
        List of paper dicts and author info dict (or None if not found).
    """
    # set email for this request
    if user_email:
        config.email = user_email
    else:
        config.email = os.environ.get("OPENALEX_EMAIL", "research@example.com")

    # search for the author
    author_results = Authors().search(author_name).get(per_page=1)

    if not author_results:
        return [], None

    # get the top matching author
    author = author_results[0]
    author_id = author.get("id")

    # extract author info for display
    author_info = {
        "display_name": author.get("display_name", "Unknown"),
        "works_count": author.get("works_count", 0),
        "cited_by_count": author.get("cited_by_count", 0),
        "last_known_institution": author.get("last_known_institution", {}).get(
            "display_name"
        )
        if author.get("last_known_institution")
        else None,
        "orcid": author.get("orcid"),
    }

    # build query for this author's works
    query = Works().filter(author={"id": author_id})

    # apply filters
    if min_year:
        query = query.filter(from_publication_date=f"{min_year}-01-01")
    if max_year:
        query = query.filter(to_publication_date=f"{max_year}-12-31")
    if open_access_only:
        query = query.filter(is_oa=True)

    # sort by citations and get results
    fetch_limit = limit * 3 if min_citations else limit
    results = query.sort(cited_by_count="desc").get(
        per_page=min(fetch_limit, 200)
    )

    # extract information from all works
    papers = [extract_paper_info(work) for work in results]

    # apply client-side citation filter if needed
    if min_citations:
        papers = [p for p in papers if p["citations"] >= min_citations]

    # return only requested number
    return papers[:limit], author_info


def display_pool_status(rate_limit_info: dict):
    """Display the pool status based on rate limit info."""
    if not rate_limit_info:
        return

    has_email = rate_limit_info.get("has_email", False)
    limit = rate_limit_info.get("rate_limit_limit", "unknown")
    remaining = rate_limit_info.get("rate_limit_remaining", "unknown")
    email = rate_limit_info.get("email_used", "")

    if has_email:
        st.success(f"""
**✓ Polite Pool - Email Sent to OpenAlex**
Email: `{email}`
OpenAlex Rate Limit: **{limit}** requests/sec | Remaining: **{remaining}**
📧 Your email is being sent to OpenAlex for better performance and to help them track usage.
        """)
    else:
        st.warning(f"""
**⚠ Common Pool - No Email Provided**
Rate Limit: **{limit}** requests/sec | Remaining: **{remaining}**
💡 Add your email in the sidebar to access the polite pool with more consistent response times.
        """)


# main app layout
# load custom font
bebas_font_base64 = load_font_base64("assets/fonts/BebasNeue-Regular.ttf")
font_css = (
    f"""
<style>
@font-face {{
    font-family: 'Bebas Neue';
    src: url(data:font/ttf;base64,{bebas_font_base64}) format('truetype');
}}
.custom-title {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    color: #0d6efd;
    margin-bottom: 0.5rem;
}}
</style>
<div class="custom-title">Citation Search</div>
"""
    if bebas_font_base64
    else """
<style>
.custom-title {{
    font-family: sans-serif;
    font-size: 3.5rem;
    color: #0d6efd;
    margin-bottom: 0.5rem;
}}
</style>
<div class="custom-title">Citation Search</div>
"""
)

st.markdown(font_css, unsafe_allow_html=True)
st.markdown("Find the most cited academic papers by keyword using OpenAlex")

# sidebar for email and filters
with st.sidebar:
    st.header("⚙️ Settings")

    # email input
    st.subheader("Email (Optional)")
    user_email = st.text_input(
        "Your email for polite pool",
        value=st.session_state.user_email,
        placeholder="your@email.com",
        help="Provide your email for faster, more consistent response times",
    )
    if user_email != st.session_state.user_email:
        st.session_state.user_email = user_email
        if user_email:
            st.success("Email saved!")

    st.divider()

    # filters
    st.subheader("🔍 Filters")

    limit = st.selectbox(
        "Number of Results", options=[5, 10, 25, 50, 100], index=1
    )

    col1, col2 = st.columns(2)
    with col1:
        min_year = st.number_input(
            "Min Year",
            min_value=1900,
            max_value=2025,
            value=None,
            placeholder="1900",
        )
    with col2:
        max_year = st.number_input(
            "Max Year",
            min_value=1900,
            max_value=2025,
            value=None,
            placeholder="2025",
        )

    min_citations = st.number_input(
        "Min Citations", min_value=0, value=None, placeholder="e.g., 100"
    )

    open_access = st.checkbox("Open Access Only")

# main search area
search_type = st.radio(
    "Search by:",
    options=["Keyword", "Author"],
    horizontal=True,
    key="search_type_radio",
)

if search_type == "Keyword":
    search_input = st.text_input(
        "Search Keyword",
        placeholder="e.g., machine learning, CRISPR, climate change",
        key="keyword_input",
    )
else:
    search_input = st.text_input(
        "Author Name",
        placeholder="e.g., Albert Einstein, Marie Curie",
        key="author_input",
    )

# search button
if st.button("🔍 Search", type="primary", use_container_width=True):
    if not search_input:
        st.error(
            f"Please enter a {'search keyword' if search_type == 'Keyword' else 'author name'}"
        )
    else:
        with st.spinner("Searching OpenAlex..."):
            try:
                if search_type == "Keyword":
                    # perform keyword search
                    papers = search_papers(
                        keyword=search_input,
                        limit=limit,
                        min_year=min_year,
                        max_year=max_year,
                        min_citations=min_citations,
                        open_access_only=open_access,
                        user_email=st.session_state.user_email
                        if st.session_state.user_email
                        else None,
                    )
                    st.session_state.author_info = None
                else:
                    # perform author search
                    papers, author_info = search_papers_by_author(
                        author_name=search_input,
                        limit=limit,
                        min_year=min_year,
                        max_year=max_year,
                        min_citations=min_citations,
                        open_access_only=open_access,
                        user_email=st.session_state.user_email
                        if st.session_state.user_email
                        else None,
                    )
                    st.session_state.author_info = author_info

                # get rate limit info
                rate_limit_info = get_openalex_rate_limit_info(
                    st.session_state.user_email
                    if st.session_state.user_email
                    else None
                )

                # store in session state
                st.session_state.search_results = papers
                st.session_state.rate_limit_info = rate_limit_info
                st.session_state.search_type = search_type

            except Exception as e:
                st.error(f"Search failed: {str(e)}")

# search tips
with st.expander("💡 Search Tips", expanded=False):
    search_tips_content = load_markdown_content("search_tips.md")
    if search_tips_content:
        st.markdown(search_tips_content)

# display results
if st.session_state.search_results is not None:
    papers = st.session_state.search_results

    # show pool status
    if st.session_state.rate_limit_info:
        display_pool_status(st.session_state.rate_limit_info)

    # show author info if this was an author search
    if st.session_state.author_info:
        author_info = st.session_state.author_info
        st.info(f"""
**Author Found:** {author_info["display_name"]}
**Institution:** {author_info["last_known_institution"] or "Unknown"}
**Total Works:** {author_info["works_count"]:,} | **Total Citations:** {author_info["cited_by_count"]:,}
{f"**ORCID:** {author_info['orcid']}" if author_info["orcid"] else ""}
        """)
        st.subheader(
            f"Found {len(papers)} papers by {author_info['display_name']}"
        )
    else:
        # results header for keyword search
        st.subheader(f"Found {len(papers)} papers")

    # download buttons
    if papers:
        col1, col2, col3 = st.columns(3)

        # prepare data for downloads
        df = pl.DataFrame(papers)

        # determine search context for file headers
        if st.session_state.author_info:
            search_context = (
                f"by {st.session_state.author_info['display_name']}"
            )
        else:
            search_context = "Citation Search Results"

        # titles only
        titles_text = f"Top {len(papers)} Papers {search_context}\n"
        titles_text += (
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )
        titles_text += "\n".join(
            [
                f"{i + 1}. {p['title']} ({p['citations']} citations)"
                for i, p in enumerate(papers)
            ]
        )

        # full text
        full_text = f"Top {len(papers)} Papers {search_context}\n"
        full_text += (
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        full_text += "=" * 80 + "\n\n"
        for i, p in enumerate(papers):
            full_text += f"{i + 1}. {p['title']}\n"
            full_text += f"   Authors: {p['authors']}\n"
            full_text += f"   Year: {p['year'] or 'Unknown'}\n"
            full_text += f"   Citations: {p['citations']}\n"
            full_text += f"   Source: {p['source']}\n"
            if p["doi"]:
                full_text += f"   DOI: {p['doi']}\n"
            if p["url"]:
                full_text += f"   URL: {p['url']}\n"
            full_text += (
                f"   Open Access: {'Yes' if p['open_access'] else 'No'}\n\n"
            )

        # csv
        csv_df = df.with_row_index("rank", offset=1)
        csv_df = csv_df.with_columns(
            pl.col("open_access").map_elements(
                lambda x: "Yes" if x else "No", return_dtype=pl.String
            )
        )
        csv_df = csv_df.select(
            [
                "rank",
                "title",
                "authors",
                "year",
                "citations",
                "source",
                "doi",
                "url",
                "open_access",
            ]
        )

        with col1:
            st.download_button(
                "📄 Download Titles (.txt)",
                data=titles_text,
                file_name="citation_titles.txt",
                mime="text/plain",
            )
        with col2:
            st.download_button(
                "📝 Download Full Data (.txt)",
                data=full_text,
                file_name="citation_full.txt",
                mime="text/plain",
            )
        with col3:
            st.download_button(
                "📊 Download Full Data (.csv)",
                data=csv_df.write_csv(),
                file_name="citation_papers.csv",
                mime="text/csv",
            )

    st.divider()

    # display papers
    for i, paper in enumerate(papers, 1):
        with st.container():
            col_main, col_citations = st.columns([4, 1])

            with col_main:
                if paper["url"]:
                    st.markdown(
                        f'**{i}. <a href="{paper["url"]}" target="_blank">{paper["title"]}</a>**',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"**{i}. {paper['title']}**", unsafe_allow_html=True
                    )

                st.caption(f"👥 {paper['authors']}")
                st.caption(
                    f"📅 {paper['year'] or 'Unknown'} | 📖 {paper['source']}"
                )

                if paper["doi"]:
                    st.caption(f"🔗 DOI: {paper['doi']}")

            with col_citations:
                st.metric("Citations", paper["citations"])
                if paper["open_access"]:
                    st.success("🔓 Open Access")

            st.divider()

# information section
with st.expander("ℹ️ About OpenAlex API Access", expanded=False):
    about_content = load_markdown_content("about_openalex.md")
    if about_content:
        st.markdown(about_content)

# comparison section
with st.expander("📊 Comparing Citation Search APIs", expanded=False):
    comparison_content = load_markdown_content("api_comparison.md")
    if comparison_content:
        st.markdown(comparison_content)

# repository and contributing section
with st.expander("🔗 Repository & Contributing", expanded=False):
    repository_content = load_markdown_content("repository_info.md")
    if repository_content:
        st.markdown(repository_content)

# footer
st.divider()
st.caption(
    "Powered by [OpenAlex](https://openalex.org) | Built with [Streamlit](https://streamlit.io)"
)
