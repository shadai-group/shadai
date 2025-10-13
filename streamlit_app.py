"""
Shadai Examples - Streamlit App
================================
Interactive demonstration of all Shadai RAG capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List

import streamlit as st

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from shadai import Shadai, tool

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Shadai Examples",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Custom CSS
# =============================================================================

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .output-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Helper Functions
# =============================================================================


async def stream_to_streamlit(generator, placeholder):
    """Stream async generator output to Streamlit with auto-scrolling.

    Args:
        generator: Async generator yielding text chunks
        placeholder: Streamlit placeholder for displaying content

    Returns:
        str: Full response text
    """
    import streamlit.components.v1 as components

    full_response = ""
    chunk_count = 0
    auto_scroll = get_auto_scroll_enabled()

    async for chunk in generator:
        full_response += chunk
        chunk_count += 1

        # Update content
        placeholder.markdown(full_response)

        # Auto-scroll every 5 chunks to reduce overhead (if enabled)
        if auto_scroll and chunk_count % 5 == 0:
            components.html(
                """
                <script>
                    const scrollToBottom = () => {
                        const mainSection = window.parent.document.querySelector('section.main');
                        if (mainSection) {
                            mainSection.scrollTop = mainSection.scrollHeight;
                        }
                    };
                    scrollToBottom();
                </script>
                """,
                height=0,
            )

    # Final scroll to ensure we're at the bottom (if enabled)
    if auto_scroll:
        components.html(
            """
            <script>
                const mainSection = window.parent.document.querySelector('section.main');
                if (mainSection) {
                    mainSection.scrollTop = mainSection.scrollHeight;
                }
            </script>
            """,
            height=0,
        )

    return full_response


def get_session_name() -> str:
    """Get or create session name."""
    if "session_name" not in st.session_state:
        st.session_state.session_name = "streamlit-session"
    return st.session_state.session_name


def get_auto_scroll_enabled() -> bool:
    """Check if auto-scroll is enabled."""
    if "auto_scroll" not in st.session_state:
        st.session_state.auto_scroll = True
    return st.session_state.auto_scroll


def add_scroll_to_bottom_button() -> None:
    """Add a button to manually scroll to bottom."""
    import streamlit.components.v1 as components

    if st.button(label="⬇️ Scroll to Bottom"):
        components.html(
            """
            <script>
                const mainSection = window.parent.document.querySelector('section.main');
                if (mainSection) {
                    mainSection.scrollTo({
                        top: mainSection.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            </script>
            """,
            height=0,
        )


# =============================================================================
# Agent Tools
# =============================================================================


@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the internal user database for information and revenue data."""
    users = [
        "John Doe - Revenue: $50,000",
        "Jane Smith - Revenue: $75,000",
        "Bob Johnson - Revenue: $60,000",
        "Alice Williams - Revenue: $85,000",
        "Charlie Brown - Revenue: $55,000",
    ]
    result = f"Database search for '{query}' (limit: {limit}):\n"
    result += "\n".join(f"  - {u}" for u in users[:limit])
    return result


@tool
def generate_report(data: str, format: str = "text") -> str:
    """Generate a professionally formatted report from raw data."""
    report = f"=== REVENUE REPORT ({format.upper()}) ===\n"
    report += data
    return report


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email message to a specified recipient."""
    return f"✓ Email sent to {recipient}: {subject}"


@tool
def get_market_data(product: str, region: str = "global") -> str:
    """Get comprehensive market analysis for a product in a specific region."""
    market_data = {
        "AI software": {
            "global": """
                Market Analysis for AI Software (Global):
                - Market Size: $142.3 billion (2023)
                - Growth Rate: 37.3% CAGR (2023-2030)
                - Key Segments: Machine Learning (45%), NLP (28%), Computer Vision (27%)
                - Top Players: OpenAI, Google, Microsoft, Anthropic
                - Adoption Rate: 35% of enterprises have implemented AI solutions
                - Investment: $93.5 billion in VC funding (2023)""",
        }
    }
    return market_data.get(product, {}).get(
        region, f"No data for {product} in {region}"
    )


@tool
def get_customer_feedback(product: str, timeframe: str = "last quarter") -> str:
    """Retrieve customer feedback, reviews, and sentiment analysis."""
    feedback_data = {
        "AI software": {
            "last quarter": """
                Customer Feedback Analysis (Q4 2024):
                Positive Feedback (78%):
                - "Significantly improved productivity by 40%"
                - "Easy integration with existing workflows"
                - "Excellent accuracy in predictions"

                Negative Feedback (22%):
                - "Initial setup complexity"
                - "Requires training for optimal use"

                Key Insights:
                - Net Promoter Score (NPS): 67 (Excellent)
                - Customer Satisfaction: 4.3/5.0
                - Retention Rate: 91%
            """,
        }
    }
    return feedback_data.get(product, {}).get(timeframe, f"No feedback for {product}")


@tool
def get_competitor_analysis(industry: str, focus: str = "pricing") -> str:
    """Analyze the competitive landscape with detailed competitor intelligence."""
    competitor_data = {
        "AI software": {
            "pricing": """
                Competitor Pricing Analysis (AI Software):
                - OpenAI GPT-4: $0.03-0.06 per 1K tokens
                - Google Vertex AI: $0.025-0.05 per 1K tokens
                - Anthropic Claude: $0.008-0.024 per 1K tokens
                - Average enterprise deal: $50K-$500K annually""",
        }
    }
    return competitor_data.get(industry, {}).get(focus, f"No analysis for {industry}")


@tool
def get_trend_analysis(topic: str, period: str = "2024") -> str:
    """Analyze industry trends, forecasts, and emerging patterns."""
    trend_data = {
        "AI adoption": {
            "2024": """
                AI Adoption Trends (2024):
                - 72% of Fortune 500 companies now use AI in production
                - Average of 3.8 AI use cases per organization
                - Top use cases: Customer service (62%), Data analytics (58%), Process automation (54%)
                - Corporate AI spending: $154 billion (34% increase)
                - Predicted market size: $190 billion by end of 2025
                """,
        }
    }
    return trend_data.get(topic, {}).get(period, f"No trends for {topic}")


# =============================================================================
# Example Functions
# =============================================================================


async def run_query_example(query: str):
    """Run RAG query example."""
    session_name = get_session_name()
    async with Shadai(name=session_name) as shadai:
        async for chunk in shadai.query(query=query):
            yield chunk


async def run_ingest_example(folder_path: str):
    """Run file ingestion example."""
    session_name = get_session_name()
    async with Shadai(name=session_name) as shadai:
        results = await shadai.ingest(folder_path=folder_path)
        return results


async def run_summary_example():
    """Run document summarization example."""
    session_name = get_session_name()
    async with Shadai(name=session_name) as shadai:
        async for chunk in shadai.summarize():
            yield chunk


async def run_websearch_example(prompt: str):
    """Run web search example."""
    session_name = get_session_name()
    async with Shadai(name=session_name) as shadai:
        async for chunk in shadai.web_search(prompt=prompt, use_web_search=True):
            yield chunk


async def run_engine_example(
    prompt: str, use_kb: bool, use_summary: bool, use_web: bool, use_memory: bool
):
    """Run engine example with multiple tools."""
    session_name = get_session_name()
    async with Shadai(name=session_name) as shadai:
        async for chunk in shadai.engine(
            prompt=prompt,
            use_knowledge_base=use_kb,
            use_summary=use_summary,
            use_web_search=use_web,
            use_memory=use_memory,
        ):
            yield chunk


async def run_simple_agent_example(prompt: str):
    """Run simple agent example."""
    session_name = get_session_name()
    tools = [search_database, generate_report, send_email]
    async with Shadai(name=session_name) as shadai:
        async for chunk in shadai.agent(prompt=prompt, tools=tools):
            yield chunk


async def run_market_agent_example(prompt: str):
    """Run market analysis agent example."""
    session_name = get_session_name()
    tools = [
        get_market_data,
        get_customer_feedback,
        get_competitor_analysis,
        get_trend_analysis,
    ]
    async with Shadai(name=session_name) as shadai:
        async for chunk in shadai.agent(prompt=prompt, tools=tools):
            yield chunk


# =============================================================================
# Main App
# =============================================================================


def main():
    """Main Streamlit app."""

    # Sidebar
    st.sidebar.markdown("# 🤖 Shadai Examples")
    st.sidebar.markdown("---")

    # Session name configuration
    st.sidebar.markdown("### Session Configuration")
    session_name = st.sidebar.text_input(
        label="Session Name",
        value=get_session_name(),
        help="Name for your RAG session",
    )
    st.session_state.session_name = session_name

    # Auto-scroll configuration
    auto_scroll = st.sidebar.checkbox(
        label="Auto-scroll during streaming",
        value=get_auto_scroll_enabled(),
        help="Automatically scroll to bottom as responses stream in",
    )
    st.session_state.auto_scroll = auto_scroll

    st.sidebar.markdown("---")

    # Example selection
    example = st.sidebar.selectbox(
        label="Select Example",
        options=[
            "🏠 Home",
            "🔍 Query",
            "📥 Ingest Files",
            "📝 Summarize",
            "🌐 Web Search",
            "🚀 Engine",
            "🤖 Simple Agent",
            "📊 Market Analysis Agent",
            "🔄 Ingest & Query",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        """
        **Shadai** is a powerful RAG (Retrieval-Augmented Generation)
        framework that combines document knowledge with AI capabilities.

        Select an example from above to get started!
        """
    )

    # Main content
    if example == "🏠 Home":
        show_home()
    elif example == "🔍 Query":
        show_query_example()
    elif example == "📥 Ingest Files":
        show_ingest_example()
    elif example == "📝 Summarize":
        show_summary_example()
    elif example == "🌐 Web Search":
        show_websearch_example()
    elif example == "🚀 Engine":
        show_engine_example()
    elif example == "🤖 Simple Agent":
        show_simple_agent_example()
    elif example == "📊 Market Analysis Agent":
        show_market_agent_example()
    elif example == "🔄 Ingest & Query":
        show_ingest_and_query_example()


# =============================================================================
# Example Pages
# =============================================================================


def show_home():
    """Show home page."""
    st.markdown(
        '<div class="main-header">🤖 Shadai Examples</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">Interactive demonstration of RAG capabilities</div>',
        unsafe_allow_html=True,
    )

    st.markdown("## 🎯 Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📚 Knowledge Base")
        st.markdown(
            """
            - **Query**: Ask questions about your documents
            - **Ingest**: Upload and process PDF and image files
            - **Summarize**: Get comprehensive document summaries
            """
        )

        st.markdown("### 🌐 Web Integration")
        st.markdown(
            """
            - **Web Search**: Get real-time information from the internet
            - **Engine**: Combine knowledge base with web search
            """
        )

    with col2:
        st.markdown("### 🤖 AI Agents")
        st.markdown(
            """
            - **Simple Agent**: Multi-tool orchestration
            - **Market Analysis**: Complex data analysis workflows
            - **Custom Tools**: Define your own agent capabilities
            """
        )

        st.markdown("### 🔄 Workflows")
        st.markdown(
            """
            - **Ingest & Query**: Complete RAG workflow
            - **Streaming**: Real-time response generation
            - **Session Management**: Persistent conversations
            """
        )

    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    st.info(
        """
        1. Select an example from the sidebar
        2. Configure the parameters
        3. Click "Run" to see the results
        4. All examples use streaming for real-time responses
        """
    )


def show_query_example():
    """Show query example page."""
    st.markdown("# 🔍 Query Example")
    st.markdown("Ask questions about your ingested documents using RAG.")

    st.markdown("---")

    query = st.text_area(
        label="Enter your query",
        value="De qué habla la quinta enmienda?",
        height=100,
        help="Ask anything about your documents",
    )

    if st.button(label="🔍 Run Query", type="primary"):
        with st.spinner("Processing query..."):
            placeholder = st.empty()
            try:
                asyncio.run(stream_to_streamlit(run_query_example(query), placeholder))
                st.success("✅ Query completed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_ingest_example():
    """Show file ingestion example page."""
    st.markdown("# 📥 Ingest Files")
    st.markdown("Upload and process documents into your knowledge base.")

    st.markdown("---")

    # Option 1: Use example data folder
    st.markdown("### Option 1: Use Example Data")
    default_path = os.path.join(os.path.dirname(__file__), "examples", "data")

    if st.button(label="📁 Ingest Example Files", type="primary"):
        if os.path.exists(default_path):
            with st.spinner("Ingesting files..."):
                try:
                    results = asyncio.run(run_ingest_example(default_path))

                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Ingestion Results")
                    st.markdown(f"**Total files**: {results['total_files']}")
                    st.markdown(f"**✓ Successful**: {results['successful_count']}")
                    st.markdown(f"**✗ Failed**: {results['failed_count']}")
                    st.markdown(f"**⊘ Skipped**: {results['skipped_count']}")
                    st.markdown("</div>", unsafe_allow_html=True)

                    if results["successful"]:
                        st.markdown("#### Successfully Ingested Files:")
                        for file_info in results["successful"]:
                            size_mb = int(file_info["size"]) / (1024 * 1024)
                            st.markdown(f"- {file_info['name']} ({size_mb:.2f} MB)")

                    if results["failed"]:
                        st.markdown("#### Failed Files:")
                        for file_info in results["failed"]:
                            st.markdown(
                                f"- {file_info['filename']}: {file_info['error']}"
                            )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.error(f"❌ Example data folder not found: {default_path}")

    st.markdown("---")

    # Option 2: Custom folder path
    st.markdown("### Option 2: Custom Folder Path")
    custom_path = st.text_input(
        label="Folder Path",
        value="",
        help="Enter the path to a folder containing PDF or image files",
    )

    if st.button(label="📂 Ingest Custom Folder"):
        if custom_path and os.path.exists(custom_path):
            with st.spinner("Ingesting files..."):
                try:
                    results = asyncio.run(run_ingest_example(custom_path))
                    st.success(f"✅ Ingested {results['successful_count']} files!")
                    st.json(results)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Please enter a valid folder path")


def show_summary_example():
    """Show summarization example page."""
    st.markdown("# 📝 Summarize Documents")
    st.markdown("Generate a comprehensive summary of all documents in your session.")

    st.markdown("---")

    st.info(
        """
        **Note**: Make sure you have ingested documents first using the
        Ingest Files example.
        """
    )

    if st.button(label="📝 Generate Summary", type="primary"):
        with st.spinner("Generating summary..."):
            placeholder = st.empty()
            try:
                asyncio.run(stream_to_streamlit(run_summary_example(), placeholder))
                st.success("✅ Summary completed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_websearch_example():
    """Show web search example page."""
    st.markdown("# 🌐 Web Search")
    st.markdown("Search the web for real-time information.")

    st.markdown("---")

    prompt = st.text_area(
        label="Enter your search query",
        value="Cuanto quedó el partido del Bayern Munchen esta semana contra Frankfurt?",
        height=100,
        help="Ask about current events, news, or any recent information",
    )

    if st.button(label="🌐 Search Web", type="primary"):
        with st.spinner("Searching the web..."):
            placeholder = st.empty()
            try:
                asyncio.run(
                    stream_to_streamlit(run_websearch_example(prompt), placeholder)
                )
                st.success("✅ Search completed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_engine_example():
    """Show engine example page."""
    st.markdown("# 🚀 Engine")
    st.markdown("Orchestrate multiple RAG capabilities for comprehensive answers.")

    st.markdown("---")

    st.markdown("### Configuration")
    col1, col2 = st.columns(2)

    with col1:
        use_kb = st.checkbox(
            label="Use Knowledge Base", value=True, help="Query documents"
        )
        use_summary = st.checkbox(
            label="Use Summary", value=True, help="Get document overview"
        )

    with col2:
        use_web = st.checkbox(
            label="Use Web Search", value=True, help="Get current information"
        )
        use_memory = st.checkbox(
            label="Use Memory", value=False, help="Store conversation context"
        )

    st.markdown("---")

    prompt = st.text_area(
        label="Enter your prompt",
        value="""Based on the documents in this session:
1. What are the main topics covered?
2. How do they relate to current industry trends?
3. Are there any contradictions with latest information?""",
        height=150,
        help="Provide a comprehensive prompt that requires multiple capabilities",
    )

    if st.button(label="🚀 Run Engine", type="primary"):
        with st.spinner("Processing with engine..."):
            placeholder = st.empty()
            try:
                asyncio.run(
                    stream_to_streamlit(
                        run_engine_example(
                            prompt, use_kb, use_summary, use_web, use_memory
                        ),
                        placeholder,
                    )
                )
                st.success("✅ Engine processing completed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_simple_agent_example():
    """Show simple agent example page."""
    st.markdown("# 🤖 Simple Agent")
    st.markdown("Demonstrate multi-tool orchestration with a simple workflow.")

    st.markdown("---")

    st.info(
        """
        **Available Tools**:
        - `search_database`: Search internal database for users
        - `generate_report`: Create formatted reports
        - `send_email`: Send email notifications
        """
    )

    prompt = st.text_area(
        label="Enter your prompt",
        value="""Find the top 5 revenue users, create a text report, and email it to
team@example.com with subject "Revenue Report" """,
        height=100,
        help="The agent will automatically select and use appropriate tools",
    )

    if st.button(label="🤖 Run Agent", type="primary"):
        with st.spinner("Agent working..."):
            placeholder = st.empty()
            try:
                asyncio.run(
                    stream_to_streamlit(run_simple_agent_example(prompt), placeholder)
                )
                st.success("✅ Agent completed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_market_agent_example():
    """Show market analysis agent example page."""
    st.markdown("# 📊 Market Analysis Agent")
    st.markdown("Complex agent workflow for comprehensive market intelligence.")

    st.markdown("---")

    st.info(
        """
        **Available Tools**:
        - `get_market_data`: Market size and growth analysis
        - `get_customer_feedback`: Customer sentiment and NPS
        - `get_competitor_analysis`: Competitive landscape
        - `get_trend_analysis`: Industry trends and forecasts
        """
    )

    prompt = st.text_area(
        label="Enter your prompt",
        value="""I need a comprehensive market analysis for AI software. Include the current
market size and growth, what customers are saying, how we compare to competitors
in terms of pricing, and what the adoption trends look like. Give me actionable
insights for strategy planning.""",
        height=150,
        help="The agent will use multiple tools to provide comprehensive analysis",
    )

    if st.button(label="📊 Run Market Analysis", type="primary"):
        with st.spinner("Analyzing market data..."):
            placeholder = st.empty()
            try:
                asyncio.run(
                    stream_to_streamlit(run_market_agent_example(prompt), placeholder)
                )
                st.success("✅ Market analysis completed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_ingest_and_query_example():
    """Show ingest and query workflow example page."""
    st.markdown("# 🔄 Ingest & Query Workflow")
    st.markdown("Complete workflow: Ingest files then query the knowledge base.")

    st.markdown("---")

    st.markdown("## Step 1: Ingest Files")
    ingest_col1, ingest_col2 = st.columns([3, 1])

    with ingest_col1:
        folder_path = st.text_input(
            label="Folder Path",
            value=os.path.join(os.path.dirname(__file__), "examples", "data"),
            help="Path to folder containing files",
        )

    with ingest_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ingest_button = st.button(label="📥 Ingest", type="primary")

    if ingest_button:
        if os.path.exists(folder_path):
            with st.spinner("Ingesting files..."):
                try:
                    results = asyncio.run(run_ingest_example(folder_path))
                    st.success(f"✅ Ingested {results['successful_count']} files!")
                    st.session_state.ingestion_done = True
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Folder path does not exist")

    st.markdown("---")

    st.markdown("## Step 2: Query Knowledge Base")

    if "ingestion_done" not in st.session_state:
        st.warning("⚠️ Please ingest files first (Step 1)")
    else:
        query = st.text_area(
            label="Enter your query",
            value="De qué habla la quinta enmienda?",
            height=100,
            help="Ask questions about the ingested documents",
        )

        if st.button(label="🔍 Query", type="primary"):
            with st.spinner("Processing query..."):
                placeholder = st.empty()
                try:
                    asyncio.run(
                        stream_to_streamlit(run_query_example(query), placeholder)
                    )
                    st.success("✅ Query completed!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# =============================================================================
# Run App
# =============================================================================

if __name__ == "__main__":
    main()
