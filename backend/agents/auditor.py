from tools.agent_tools import mock_audit_transaction
from pydantic import BaseModel
from agents import Agent

AUDITOR_PROMPT = (
    "You are the Auditor. Use the provided tool to verify the transaction by id and report confirmation."
)

class AuditorSummary(BaseModel):
    summary: str 
    """Short text summary for this aspect of the analysis."""

def build_auditor_agent() -> Agent:
    audit_tool = mock_audit_transaction
    agent = Agent(
    name="AuditorAgent",
    instructions=AUDITOR_PROMPT,
    tools=[audit_tool],
    )
    return agent