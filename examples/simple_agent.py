import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Session, Shadai, tool
from shadai.timing import timed


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


@timed
async def main() -> None:
    shadai = Shadai()

    tools = [search_database, generate_report, send_email]

    prompt = """
    Find the top 5 revenue users, create a text report, and email it to
    team@example.com with subject "Revenue Report"
    """

    async with Session(name="test 6") as session:
        async for chunk in shadai.agent(prompt=prompt, tools=tools, session=session):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
