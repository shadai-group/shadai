"""
Shadai Agent Examples
---------------------
Demonstrates the intelligent agent workflow with various scenarios:
1. Simple multi-tool orchestration
2. Complex market analysis with multiple data sources
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai, tool
from shadai.timing import timed


# =============================================================================
# Simple Agent Tools
# =============================================================================


@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the internal user database for information and revenue data.

    Returns user records sorted by revenue with detailed financial metrics.
    Use this tool when you need to find users, analyze revenue patterns,
    or identify top performers.

    Args:
        query: Search query string to filter user records. Can include
            keywords like "revenue", "top users", "sales", "high performers".
        limit: Maximum number of user records to return in the results.
            Default is 10. Use smaller values (3-5) for summaries,
            larger values (10-20) for comprehensive analysis.

    Returns:
        Formatted string containing user records with names and revenue figures.
    """
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
    """Generate a professionally formatted report from raw data.

    Creates structured output with headers, timestamps, and proper formatting.
    Supports multiple output formats including plain text, HTML, and markdown.
    Use this tool to transform raw data into presentation-ready reports.

    Args:
        data: Raw data content to include in the report. Should contain
            the information that needs to be formatted (e.g., user lists,
            statistics, analysis results, summaries). Can be multi-line text
            with structured information.
        format: Output format for the report. Options: "text" for plain text
            with headers (default), "html" for web-ready HTML with styling,
            "markdown" for documentation-friendly format. Choose based on
            how the report will be used or displayed.

    Returns:
        Formatted report string with headers, timestamp, and structured content.
    """
    report = f"=== REVENUE REPORT ({format.upper()}) ===\n"
    report += data
    return report


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email message to a specified recipient with subject and body content.

    Delivers messages to team members, stakeholders, or any email address.
    Use this tool to communicate results, share reports, or send notifications.

    Args:
        recipient: Email address of the recipient who will receive the message.
            Must be a valid email format (e.g., user@example.com, team@company.org).
            Can be an individual or team distribution list.
        subject: Subject line for the email. Should be concise and descriptive.
            Keep under 60 characters for best display in email clients.
        body: Main content of the email message. Can include formatted text,
            data summaries, analysis results, or any information to communicate.
            Be clear and professional. Can be multi-line text with line breaks.

    Returns:
        Confirmation message indicating successful email delivery with recipient
        address and subject line.
    """
    return f"✓ Email sent to {recipient}: {subject}"


# =============================================================================
# Market Analysis Tools
# =============================================================================


@tool
def get_market_data(product: str, region: str = "global") -> str:
    """Get comprehensive market analysis for a product in a specific region.

    Retrieves detailed market intelligence including market size, growth rates,
    key market segments, major players, adoption statistics, and investment data.

    Args:
        product: Product category to analyze. Examples: "AI software", "cloud storage",
            "SaaS platforms". The analysis focuses on this specific product vertical.
        region: Geographic region for market analysis. Supported regions:
            "global" for worldwide market data (default), "north america" for
            US/Canada/Mexico market focus, "europe" for European market trends,
            "asia" for Asia-Pacific region analysis.

    Returns:
        Formatted string containing comprehensive market analysis with metrics.
    """
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
            "north america": """
                Market Analysis for AI Software (North America):
                - Market Size: $51.2 billion (2023)
                - Growth Rate: 35.8% CAGR
                - Leading Adopters: Technology (68%), Finance (52%), Healthcare (43%)
                - Key Drivers: Digital transformation, automation, cost reduction
            """,
        }
    }
    return market_data.get(product, {}).get(
        region, f"No data for {product} in {region}"
    )


@tool
def get_customer_feedback(product: str, timeframe: str = "last quarter") -> str:
    """Retrieve customer feedback, reviews, and comprehensive sentiment analysis.

    Aggregates and analyzes customer feedback from multiple sources including
    reviews, surveys, support tickets, and social media mentions. Provides
    quantitative metrics and qualitative insights.

    Args:
        product: Product name to analyze feedback for. Must match a product
            in the system (e.g., "AI software", "cloud platform").
        timeframe: Time period for feedback collection and analysis. Options:
            "last quarter" for most recent 3-month period (default),
            "last year" for previous 12 months, "last month" for most recent 30 days.

    Returns:
        Formatted string containing detailed feedback analysis including NPS,
        satisfaction scores, and sentiment themes.
    """
    feedback_data = {
        "AI software": {
            "last quarter": """
                Customer Feedback Analysis (Q4 2024):
                Positive Feedback (78%):
                - "Significantly improved productivity by 40%"
                - "Easy integration with existing workflows"
                - "Excellent accuracy in predictions"
                - "Strong customer support and documentation"
                - "Cost-effective compared to hiring additional staff"

                Negative Feedback (22%):
                - "Initial setup complexity"
                - "Requires training for optimal use"
                - "Some features have steep learning curve"
                - "Occasional latency issues during peak hours"

                Key Insights:
                - Net Promoter Score (NPS): 67 (Excellent)
                - Customer Satisfaction: 4.3/5.0
                - Feature Requests: Better mobile support, more customization options
                - Retention Rate: 91%
            """,
        }
    }
    return feedback_data.get(product, {}).get(timeframe, f"No feedback for {product}")


@tool
def get_competitor_analysis(industry: str, focus: str = "pricing") -> str:
    """Analyze the competitive landscape with detailed competitor intelligence.

    Provides comprehensive analysis of competitors including pricing strategies,
    feature comparisons, market positioning, and competitive advantages/disadvantages.

    Args:
        industry: Industry sector to analyze competitors in. Examples:
            "AI software", "SaaS", "cloud computing", "fintech".
            The analysis focuses on key players in this industry.
        focus: Specific aspect of competitive analysis to emphasize. Options:
            "pricing" for price points and tiers (default), "features" for
            capability comparison, "market share" for market position analysis,
            "technology" for technical capabilities and infrastructure.

    Returns:
        Formatted string containing detailed competitive analysis with pricing,
        features, and market positioning insights.
    """
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
            "features": """Competitor Feature Comparison:

                    OpenAI GPT-4:
                    + Best-in-class language understanding
                    + Multimodal capabilities (text + vision)
                    - Higher cost, API rate limits

                    Google Vertex AI:
                    + Strong integration with GCP
                    + Custom model training
                    - Complex setup, vendor lock-in

                    Anthropic Claude:
                    + Longest context window (100K tokens)
                    + Strong safety features
                    - Limited availability, newer platform

                    Market Gaps:
                    - Real-time processing
                    - Industry-specific fine-tuning
                    - Enhanced data privacy options
                """,
        }
    }
    return competitor_data.get(industry, {}).get(focus, f"No analysis for {industry}")


@tool
def get_trend_analysis(topic: str, period: str = "2024") -> str:
    """Analyze industry trends, forecasts, and emerging patterns.

    Provides comprehensive trend analysis covering adoption rates, technology
    evolution, investment patterns, challenges, and future outlook for the
    specified industry or technology topic.

    Args:
        topic: Topic or industry to analyze trends for. Examples:
            "AI adoption", "cloud computing", "digital transformation",
            "cybersecurity trends". Focus should be on a specific trend area.
        period: Time period for trend analysis. Options:
            "2024" for current year analysis (default), "2023-2024" for
            two-year trend comparison, "2025" for forward-looking predictions.
            Can be a year or year range.

    Returns:
        Formatted string containing comprehensive trend analysis with adoption
        statistics, technology trends, investment patterns, and future outlook.
    """
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
# Example Scenarios
# =============================================================================


@timed
async def simple_agent_example() -> None:
    """Simple agent example: Database search, report generation, and email."""
    tools = [search_database, generate_report, send_email]

    prompt = """
    Find the top 5 revenue users, create a text report, and email it to
    team@example.com with subject "Revenue Report"
    """

    async with Shadai(name="test") as shadai:
        async for chunk in shadai.agent(prompt=prompt, tools=tools):
            print(chunk, end="", flush=True)


@timed
async def market_analysis_example() -> None:
    """Complex agent example: Comprehensive market analysis."""
    tools = [
        get_market_data,
        get_customer_feedback,
        get_competitor_analysis,
        get_trend_analysis,
    ]

    prompt = """
    I need a comprehensive market analysis for AI software. Include the current
    market size and growth, what customers are saying, how we compare to competitors
    in terms of pricing, and what the adoption trends look like. Give me actionable
    insights for strategy planning.
    """

    async with Shadai(name="test") as shadai:
        async for chunk in shadai.agent(prompt=prompt, tools=tools):
            print(chunk, end="", flush=True)


async def main() -> None:
    """Run all agent examples."""
    await simple_agent_example()
    await market_analysis_example()


if __name__ == "__main__":
    asyncio.run(main())
