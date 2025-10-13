"""
Shadai Examples Chat Interface - Streamlit App
===============================================
Chat-based interface for all Shadai examples.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict

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
    .main-title {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Example Configurations
# =============================================================================

EXAMPLES = {
    "Query": {
        "icon": "💬",
        "title": "Query Example",
        "description": "Ask questions about your documents using RAG",
        "session_name": "test",
        "requires_input": True,
    },
    "Summary": {
        "icon": "📝",
        "title": "Summary Example",
        "description": "Summarize all documents in the session",
        "session_name": "test",
        "requires_input": False,
    },
    "Web Search": {
        "icon": "🌐",
        "title": "Web Search Example",
        "description": "Search the web for current information",
        "session_name": "test",
        "requires_input": True,
    },
    "Engine": {
        "icon": "🚀",
        "title": "Engine Example",
        "description": "Multi-tool orchestration with knowledge base, summary, web search, and memory",
        "session_name": "test",
        "use_knowledge_base": True,
        "use_summary": True,
        "use_web_search": True,
        "use_memory": False,
        "requires_input": True,
    },
    "Simple Agent": {
        "icon": "🤖",
        "title": "Simple Agent Example",
        "description": "Agent with database search, report generation, and email tools",
        "session_name": "test",
        "requires_input": True,
    },
    "Market Agent": {
        "icon": "📊",
        "title": "Market Agent Example",
        "description": "Comprehensive market analysis with multiple data sources",
        "session_name": "test",
        "requires_input": True,
    },
    "Ingest": {
        "icon": "📁",
        "title": "Ingest Example",
        "description": "Ingest files from a folder into a RAG session",
        "default_folder": os.path.join(os.path.dirname(__file__), "examples", "data"),
        "session_name": "test",
        "requires_input": False,
    },
}

# =============================================================================
# Session State Initialization
# =============================================================================


def init_session_state():
    """Initialize session state variables."""
    if "current_example" not in st.session_state:
        st.session_state.current_example = "Query"

    # Initialize message history for each example
    for example_name in EXAMPLES.keys():
        if f"messages_{example_name}" not in st.session_state:
            st.session_state[f"messages_{example_name}"] = []

    # Initialize ingestion status for each example
    for example_name in ["Ingest"]:
        if f"ingested_{example_name}" not in st.session_state:
            st.session_state[f"ingested_{example_name}"] = False

    # Initialize session names for each example (editable)
    for example_name, config in EXAMPLES.items():
        if f"session_name_{example_name}" not in st.session_state:
            st.session_state[f"session_name_{example_name}"] = config["session_name"]


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
- "Strong customer support and documentation"

Negative Feedback (22%):
- "Initial setup complexity"
- "Requires training for optimal use"
- "Some features have steep learning curve"

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
Premium Tier Competitors:
- OpenAI GPT-4: $0.03-0.06 per 1K tokens, Enterprise: Custom pricing
- Google Vertex AI: $0.025-0.05 per 1K tokens
- Anthropic Claude: $0.008-0.024 per 1K tokens

Mid-Tier Competitors:
- Cohere: $0.015-0.035 per 1K tokens
- AI21 Labs: $0.01-0.03 per 1K tokens

Open Source Alternatives:
- Llama 2: Free (self-hosting costs apply)
- Mistral: Free/Premium hybrid model

Market Positioning:
- Premium segment: 15-20% price premium justified by performance
- Value segment: 30-40% lower pricing, trade-off on features
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
Enterprise Adoption:
- 72% of Fortune 500 companies now use AI in production
- Average of 3.8 AI use cases per organization (up from 2.1 in 2023)
- Top use cases: Customer service automation (62%), Data analytics (58%), Process automation (54%)

Technology Trends:
- Generative AI dominates: 89% of AI projects involve GenAI
- Multi-modal AI growing 156% year-over-year
- Edge AI deployment increased 43%
- Responsible AI frameworks adopted by 67% of enterprises

Investment Trends:
- Corporate AI spending: $154 billion (34% increase)
- Focus shifting from experimentation to production deployment
- ROI expectations: 82% expect positive ROI within 12 months

Challenges:
- Talent shortage: 71% cite lack of AI expertise
- Data quality issues: 58% struggle with data preparation
- Integration complexity: 49% face legacy system challenges

Future Outlook:
- Predicted market size: $190 billion by end of 2025
- Expected annual growth: 35-40% through 2027
- Regulatory frameworks emerging in EU, US, and Asia
                """,
        }
    }
    return trend_data.get(topic, {}).get(period, f"No trends for {topic}")


# =============================================================================
# Processing Functions
# =============================================================================


async def process_query(
    example: str, prompt: str, config: Dict
) -> AsyncGenerator[str, None]:
    """Process user query based on selected example."""
    session_name = st.session_state[f"session_name_{example}"]

    async with Shadai(name=session_name) as shadai:
        if example == "Query":
            async for chunk in shadai.query(query=prompt):
                yield chunk

        elif example == "Summary":
            async for chunk in shadai.summarize():
                yield chunk

        elif example == "Web Search":
            async for chunk in shadai.web_search(prompt=prompt, use_web_search=True):
                yield chunk

        elif example == "Engine":
            async for chunk in shadai.engine(
                prompt=prompt,
                use_knowledge_base=config.get("use_knowledge_base", True),
                use_summary=config.get("use_summary", True),
                use_web_search=config.get("use_web_search", True),
                use_memory=config.get("use_memory", False),
            ):
                yield chunk

        elif example == "Simple Agent":
            tools = [search_database, generate_report, send_email]
            async for chunk in shadai.agent(prompt=prompt, tools=tools):
                yield chunk

        elif example == "Market Agent":
            tools = [
                get_market_data,
                get_customer_feedback,
                get_competitor_analysis,
                get_trend_analysis,
            ]
            async for chunk in shadai.agent(prompt=prompt, tools=tools):
                yield chunk


async def stream_response(example: str, prompt: str, config: Dict) -> str:
    """Stream response and return full text."""
    full_response = ""
    response_placeholder = st.empty()

    async for chunk in process_query(example=example, prompt=prompt, config=config):
        full_response += chunk
        response_placeholder.markdown(full_response)

    return full_response


async def ingest_files(folder_path: str, session_name: str) -> Dict:
    """Ingest files from folder."""
    async with Shadai(name=session_name) as shadai:
        results = await shadai.ingest(folder_path=folder_path)
        return results


# =============================================================================
# UI Components
# =============================================================================


def show_example_controls(example: str, config: Dict):
    """Show example-specific controls."""

    if example == "Engine":
        st.markdown("### Engine Configuration")
        col1, col2 = st.columns(2)
        with col1:
            use_knowledge_base = st.checkbox(
                label="Use Knowledge Base",
                value=config.get("use_knowledge_base", True),
                help="Query specific content from documents",
            )
            use_summary = st.checkbox(
                label="Use Summary",
                value=config.get("use_summary", True),
                help="Get overview of all documents",
            )
        with col2:
            use_web_search = st.checkbox(
                label="Use Web Search",
                value=config.get("use_web_search", True),
                help="Get latest trends and information",
            )
            use_memory = st.checkbox(
                label="Use Memory",
                value=config.get("use_memory", False),
                help="Store and retrieve conversation context",
            )

        config["use_knowledge_base"] = use_knowledge_base
        config["use_summary"] = use_summary
        config["use_web_search"] = use_web_search
        config["use_memory"] = use_memory

        st.markdown("---")

    elif example in ["Ingest"]:
        st.markdown("### Folder Configuration")

        default_folder = config.get("default_folder", "")
        folder_path = st.text_input(
            label="Folder Path",
            value=default_folder,
            help="Path to folder containing PDF or image files",
            key=f"folder_path_{example}",
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(
                label="📁 Ingest Files", type="primary", key=f"ingest_btn_{example}"
            ):
                if os.path.exists(folder_path):
                    with st.spinner("Ingesting files..."):
                        try:
                            results = asyncio.run(
                                ingest_files(
                                    folder_path=folder_path,
                                    session_name=st.session_state[
                                        f"session_name_{example}"
                                    ],
                                )
                            )
                            st.session_state[f"ingested_{example}"] = True

                            # Add system message
                            message = f"""✅ **Ingestion Complete**

**Results:**
- Total files: {results["total_files"]}
- ✓ Successful: {results["successful_count"]}
- ✗ Failed: {results["failed_count"]}
- ⊘ Skipped: {results["skipped_count"]}
"""
                            if results["successful"]:
                                message += "\n**Files ingested:**\n"
                                for file_info in results["successful"]:
                                    size_mb = int(file_info["size"]) / (1024 * 1024)
                                    message += (
                                        f"- {file_info['name']} ({size_mb:.2f} MB)\n"
                                    )

                            st.session_state[f"messages_{example}"].append(
                                {"role": "assistant", "content": message}
                            )
                            st.success("Files ingested successfully!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Folder path does not exist")

        with col2:
            if st.session_state.get(f"ingested_{example}", False):
                st.success("✅ Files ingested")
            else:
                st.info("⚠️ No files ingested yet")

        st.markdown("---")


# =============================================================================
# Main App
# =============================================================================


def main():
    """Main chat interface."""
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.markdown("# 🤖 Shadai Examples")
        st.markdown("---")

        # Example selection
        st.markdown("### 📚 Select Example")

        selected_example = st.radio(
            label="Example",
            options=list(EXAMPLES.keys()),
            format_func=lambda x: f"{EXAMPLES[x]['icon']} {x}",
            index=list(EXAMPLES.keys()).index(st.session_state.current_example),
            label_visibility="collapsed",
        )
        st.session_state.current_example = selected_example

        st.markdown("---")

        # Example description
        st.markdown("### 📖 Description")
        st.info(EXAMPLES[selected_example]["description"])

        st.markdown("---")

        # Session name (editable)
        st.markdown("### ⚙️ Session")
        session_name = st.text_input(
            label="Session Name",
            value=st.session_state[f"session_name_{selected_example}"],
            help="Edit to use a different session",
            key=f"session_input_{selected_example}",
        )
        # Update session state when changed
        st.session_state[f"session_name_{selected_example}"] = session_name

        st.markdown("---")

        # Clear chat button
        if st.button(label="🗑️ Clear Chat", use_container_width=True):
            st.session_state[f"messages_{selected_example}"] = []
            st.rerun()

    # Main content area
    example_config = EXAMPLES[selected_example].copy()

    st.markdown(
        f'<div class="main-title">{example_config["icon"]} {example_config["title"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="subtitle">{example_config["description"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Show example-specific controls
    show_example_controls(example=selected_example, config=example_config)

    # Display chat messages
    messages = st.session_state[f"messages_{selected_example}"]
    for message in messages:
        with st.chat_message(name=message["role"]):
            st.markdown(message["content"])

    # Handle input based on example type
    if selected_example == "Summary":
        # Summary doesn't need input - just a button
        if st.button(
            label="📝 Generate Summary", type="primary", use_container_width=True
        ):
            # Add placeholder message
            st.session_state[f"messages_{selected_example}"].append(
                {"role": "user", "content": "Generate summary of all documents"}
            )

            with st.chat_message(name="user"):
                st.markdown("Generate summary of all documents")

            # Generate summary
            with st.chat_message(name="assistant"):
                try:
                    response = asyncio.run(
                        stream_response(
                            example=selected_example, prompt="", config=example_config
                        )
                    )
                    st.session_state[f"messages_{selected_example}"].append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[f"messages_{selected_example}"].append(
                        {"role": "assistant", "content": error_msg}
                    )

    elif selected_example == "Ingest":
        # Ingest example only shows the ingest UI (no chat input needed)
        st.info(
            "💡 Use the folder configuration above to ingest files. Results will appear in the chat."
        )

    else:
        # Regular chat input for examples that need text input
        if prompt := st.chat_input(placeholder="Ask a question..."):
            # Add user message to chat
            st.session_state[f"messages_{selected_example}"].append(
                {"role": "user", "content": prompt}
            )

            # Display user message
            with st.chat_message(name="user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message(name="assistant"):
                try:
                    response = asyncio.run(
                        stream_response(
                            example=selected_example,
                            prompt=prompt,
                            config=example_config,
                        )
                    )
                    st.session_state[f"messages_{selected_example}"].append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[f"messages_{selected_example}"].append(
                        {"role": "assistant", "content": error_msg}
                    )


# =============================================================================
# Run App
# =============================================================================

if __name__ == "__main__":
    main()
