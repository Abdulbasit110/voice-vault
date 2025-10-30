from tools.agent_tools import security_validate
from agents import Agent

def build_security_validator_agent() -> Agent:
    sec_tool = security_validate
    instructions = (
        "You are the Security Validator. Use the provided tool to validate destination addresses, "
        "amount ranges, and supported assets."
    )
    agent = Agent(
        name="SecurityValidatorAgent",
        instructions=instructions,
        tools=[sec_tool],
        model="gpt-4o-mini",
    )
    return agent
