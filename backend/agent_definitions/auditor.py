import os
import sys

# Add the backend directory to Python path for Vercel serverless
# This must be done BEFORE importing local modules
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

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