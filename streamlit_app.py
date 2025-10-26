"""
Streamlit web application to find top cited papers using OpenAlex.

This application provides an interface for searching the most cited
academic papers by keyword using the OpenAlex API.
"""

import streamlit as st
from pyalex import Works, config
import requests
import polars as pl
from datetime import datetime
import os


# page configuration
st.set_page_config(
    page_title="Citation Search",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# initialize session state
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "rate_limit_info" not in st.session_state:
    st.session_state.rate_limit_info = None


def get_openalex_rate_limit_info(user_email: str | None = None) -> dict:
    """
    make a test request to OpenAlex to get rate limit headers.

    Parameters
    ----------
    user_email : str | None
        user email for polite pool

    Returns
    -------
    dict
        rate limit information from OpenAlex headers
    """
    email = user_email or os.environ.get("OPENALEX_EMAIL", "research@example.com")

    url = "https://api.openalex.org/works"
    params = {"per-page": 1, "mailto": email}

    try:
        response = requests.get(url, params=params, timeout=5)
        headers = response.headers

        limit = headers.get("ratelimit-limit", headers.get("x-ratelimit-limit", "unknown"))
        remaining = headers.get("ratelimit-remaining", headers.get("x-ratelimit-remaining", "unknown"))

        return {
            "rate_limit_limit": limit,
            "rate_limit_remaining": remaining,
            "email_used": email,
            "has_email": bool(user_email)
        }
    except Exception as e:
        return {
            "error": str(e),
            "email_used": email,
            "has_email": bool(user_email)
        }


def extract_paper_info(work: dict) -> dict:
    """
    extract relevant fields from a work object.

    Parameters
    ----------
    work : dict
        work object from OpenAlex API

    Returns
    -------
    dict
        extracted paper information
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
        "source": source.get("display_name", "Unknown")
    }


def search_papers(keyword: str, limit: int = 25, min_year: int | None = None,
                  max_year: int | None = None, min_citations: int | None = None,
                  open_access_only: bool = False, user_email: str | None = None) -> list[dict]:
    """
    search OpenAlex for top cited papers by keyword.

    Parameters
    ----------
    keyword : str
        search keyword
    limit : int
        number of results to return
    min_year : int | None
        minimum publication year
    max_year : int | None
        maximum publication year
    min_citations : int | None
        minimum citation count
    open_access_only : bool
        only return open access papers
    user_email : str | None
        user email for polite pool access

    Returns
    -------
    list[dict]
        list of paper dicts
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
    results = query.sort(cited_by_count="desc").get(per_page=min(fetch_limit, 200))

    # extract information from all works
    papers = [extract_paper_info(work) for work in results]

    # apply client-side citation filter if needed
    if min_citations:
        papers = [p for p in papers if p["citations"] >= min_citations]

    # return only requested number
    return papers[:limit]


def display_pool_status(rate_limit_info: dict):
    """display the pool status based on rate limit info."""
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
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
.custom-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    color: #0d6efd;
    margin-bottom: 0.5rem;
}
</style>
<div class="custom-title">Citation Search</div>
""", unsafe_allow_html=True)
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
        help="Provide your email for faster, more consistent response times"
    )
    if user_email != st.session_state.user_email:
        st.session_state.user_email = user_email
        if user_email:
            st.success("Email saved!")

    st.divider()

    # filters
    st.subheader("🔍 Filters")

    limit = st.selectbox(
        "Number of Results",
        options=[5, 10, 25, 50, 100],
        index=1
    )

    col1, col2 = st.columns(2)
    with col1:
        min_year = st.number_input(
            "Min Year",
            min_value=1900,
            max_value=2025,
            value=None,
            placeholder="1900"
        )
    with col2:
        max_year = st.number_input(
            "Max Year",
            min_value=1900,
            max_value=2025,
            value=None,
            placeholder="2025"
        )

    min_citations = st.number_input(
        "Min Citations",
        min_value=0,
        value=None,
        placeholder="e.g., 100"
    )

    open_access = st.checkbox("Open Access Only")

# main search area
keyword = st.text_input(
    "Search Keyword",
    placeholder="e.g., machine learning, CRISPR, climate change"
)

# search button
if st.button("🔍 Search", type="primary", use_container_width=True):
    if not keyword:
        st.error("Please enter a search keyword")
    else:
        with st.spinner("Searching OpenAlex..."):
            try:
                # perform search
                papers = search_papers(
                    keyword=keyword,
                    limit=limit,
                    min_year=min_year,
                    max_year=max_year,
                    min_citations=min_citations,
                    open_access_only=open_access,
                    user_email=st.session_state.user_email if st.session_state.user_email else None
                )

                # get rate limit info
                rate_limit_info = get_openalex_rate_limit_info(
                    st.session_state.user_email if st.session_state.user_email else None
                )

                # store in session state
                st.session_state.search_results = papers
                st.session_state.rate_limit_info = rate_limit_info

            except Exception as e:
                st.error(f"Search failed: {str(e)}")

# search tips
with st.expander("💡 Search Tips", expanded=False):
    st.markdown("""
    - Use quotes for exact phrases: `"machine learning"`
    - More specific keywords = narrower, more relevant results
    - Use year filters to focus on recent breakthroughs or historical work
    - Set minimum citations to find highly influential papers
    - Enable "Open Access" to find papers you can read immediately
    """)

# display results
if st.session_state.search_results is not None:
    papers = st.session_state.search_results

    # show pool status
    if st.session_state.rate_limit_info:
        display_pool_status(st.session_state.rate_limit_info)

    # results header
    st.subheader(f"Found {len(papers)} papers for '{keyword}'")

    # download buttons
    if papers:
        col1, col2, col3 = st.columns(3)

        # prepare data for downloads
        df = pl.DataFrame(papers)

        # titles only
        titles_text = f"Top {len(papers)} Papers for '{keyword}'\n"
        titles_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        titles_text += "\n".join([
            f"{i+1}. {p['title']} ({p['citations']} citations)"
            for i, p in enumerate(papers)
        ])

        # full text
        full_text = f"Top {len(papers)} Papers for '{keyword}'\n"
        full_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_text += "=" * 80 + "\n\n"
        for i, p in enumerate(papers):
            full_text += f"{i+1}. {p['title']}\n"
            full_text += f"   Authors: {p['authors']}\n"
            full_text += f"   Year: {p['year'] or 'Unknown'}\n"
            full_text += f"   Citations: {p['citations']}\n"
            full_text += f"   Source: {p['source']}\n"
            if p['doi']:
                full_text += f"   DOI: {p['doi']}\n"
            if p['url']:
                full_text += f"   URL: {p['url']}\n"
            full_text += f"   Open Access: {'Yes' if p['open_access'] else 'No'}\n\n"

        # csv
        csv_df = df.with_row_index("rank", offset=1)
        csv_df = csv_df.with_columns(
            pl.col("open_access").map_elements(lambda x: "Yes" if x else "No", return_dtype=pl.String)
        )
        csv_df = csv_df.select(['rank', 'title', 'authors', 'year', 'citations', 'source', 'doi', 'url', 'open_access'])

        with col1:
            st.download_button(
                "📄 Download Titles (.txt)",
                data=titles_text,
                file_name="citation_titles.txt",
                mime="text/plain"
            )
        with col2:
            st.download_button(
                "📝 Download Full Data (.txt)",
                data=full_text,
                file_name="citation_full.txt",
                mime="text/plain"
            )
        with col3:
            st.download_button(
                "📊 Download Full Data (.csv)",
                data=csv_df.write_csv(),
                file_name="citation_papers.csv",
                mime="text/csv"
            )

    st.divider()

    # display papers
    for i, paper in enumerate(papers, 1):
        with st.container():
            col_main, col_citations = st.columns([4, 1])

            with col_main:
                if paper['url']:
                    st.markdown(f"**{i}. <a href=\"{paper['url']}\" target=\"_blank\">{paper['title']}</a>**", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{i}. {paper['title']}**", unsafe_allow_html=True)

                st.caption(f"👥 {paper['authors']}")
                st.caption(f"📅 {paper['year'] or 'Unknown'} | 📖 {paper['source']}")

                if paper['doi']:
                    st.caption(f"🔗 DOI: {paper['doi']}")

            with col_citations:
                st.metric("Citations", paper['citations'])
                if paper['open_access']:
                    st.success("🔓 Open Access")

            st.divider()

# information section
with st.expander("ℹ️ About OpenAlex API Access", expanded=False):
    st.markdown("""
    ### About OpenAlex API Access

    This application uses the free [OpenAlex API](https://openalex.org) to search over 250 million academic papers. No API key is required.

    #### Why API Rate Limits Matter

    OpenAlex uses a two-tier system to ensure fair access for all users. Here's what you need to know:

    > The OpenAlex API doesn't require authentication. However, it is helpful for us to know who's behind each API call, for two reasons:
    >
    > 1. It allows us to get in touch with the user if something's gone wrong--for instance, their script has run amok and we've needed to start blocking or throttling their usage.
    >
    > 2. It lets us report back to our funders, which helps us keep the lights on.
    >
    > Like Crossref (whose approach we are shamelessly stealing), we separate API users into two pools, the **polite pool** and the **common pool**. The polite pool has more consistent response times. It's where you want to be.
    >
    > To get into the polite pool, you just have to give us an email where we can contact you. You can give us this email in one of two ways:
    >
    > 1. Add the `mailto=you@example.com` parameter in your API request, like this: `https://api.openalex.org/works?mailto=you@example.com`
    >
    > 2. Add `mailto:you@example.com` somewhere in your User-Agent request header.
    >
    > Source: [OpenAlex API Documentation](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication)

    #### For This Application

    Simply enter your email in the sidebar to access the "polite pool" with faster, more consistent response times. Your email is only sent to OpenAlex and stored in your browser session.
    """)

# comparison section
with st.expander("📊 Comparing Citation Search APIs", expanded=False):
    st.markdown("""
    ### OpenAlex vs CrossRef vs Google Scholar

    #### [OpenAlex](https://openalex.org)
    - **Coverage**: 250M+ works across all disciplines.
    - **API Access**: Free, no API key required.
    - **Rate Limits**: Polite pool (with email) gets better performance.
    - **Data Quality**: Open source, includes citation counts, author info, institutions.
    - **Documentation**: [OpenAlex Docs](https://docs.openalex.org).

    #### [CrossRef](https://www.crossref.org)
    - **Coverage**: 140M+ works with DOIs (mainly published articles).
    - **API Access**: Free, no API key required.
    - **Rate Limits**: Polite pool system (same as OpenAlex).
    - **Data Quality**: High quality metadata, DOI authority, extensive publisher data.
    - **Documentation**: [CrossRef API Docs](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).

    #### [Google Scholar](https://scholar.google.com)
    - **Coverage**: Largest index (exact size unknown, estimated 400M+).
    - **API Access**: No official API (scraping violates Terms of Service).
    - **Rate Limits**: N/A - no official API.
    - **Data Quality**: Broadest coverage but includes preprints, theses, patents.
    """)

# footer
st.divider()
st.caption("Powered by [OpenAlex](https://openalex.org) | Built with [Streamlit](https://streamlit.io)")
