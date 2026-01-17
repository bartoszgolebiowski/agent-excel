from __future__ import annotations
import os
import sys
import time
from datetime import datetime

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.agent import Agent
from src.memory import create_initial_state
from src.engine.types import WorkflowStage


def run_email_processing_cycle(agent: Agent) -> None:
    """Run one cycle of email processing."""
    print(f"\n{'='*60}")
    print(f"Email Processing Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Create initial state starting from CHECK_INBOX stage
    from src.memory.models import WorkflowMemory

    workflow = WorkflowMemory(
        goal="Process emails from inbox folder", current_stage=WorkflowStage.CHECK_INBOX
    )
    state = create_initial_state(workflow=workflow)

    # Run the agent with the email processing state
    from src.engine import AgentActionCoordinator
    from src.engine.decision import ActionType
    from src.memory.state_manager import update_state_from_skill, update_state_from_tool
    from src.logger import get_agent_logger

    logger = get_agent_logger()
    coordinator = AgentActionCoordinator()
    max_steps = 1000

    for step in range(max_steps):
        decision = coordinator.next_action(state)

        if decision.action_type == ActionType.COMPLETE:
            print(f"\n✓ Cycle completed: {decision.reason}")
            break

        if decision.action_type == ActionType.NOOP:
            print(f"\n○ No operation: {decision.reason}")
            break

        if decision.action_type == ActionType.LLM_SKILL and decision.skill:
            print(f"  → Analyzing email with AI...")
            context = agent._build_prompt_context(state)
            output = agent._llm_call(decision.skill, context)
            state = update_state_from_skill(state, decision.skill, output)
            continue

        if decision.action_type == ActionType.TOOL and decision.tool_type:
            print(f"  → Executing: {decision.reason}")
            output = agent._execute_tool(state, decision.tool_type)
            state = update_state_from_tool(state, decision.tool_type, output)
            continue

    # Print summary
    processed = state.working.email_processing.processed_count
    print(f"\n{'='*60}")
    print(f"Cycle Summary: {processed} email(s) processed")
    print(f"{'='*60}\n")


def main():
    """Run the email processing agent."""
    # Attempt to load environment variables from .env
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    try:
        # Initialize the agent from environment configuration
        agent = Agent.from_env()

        # Check if we should run in cyclic mode
        cyclic_mode = os.getenv("CYCLIC_MODE", "false").lower() == "true"
        cycle_interval = int(
            os.getenv("CYCLE_INTERVAL_SECONDS", "3600")
        )  # Default 1 hour

        if cyclic_mode:
            print("\n" + "=" * 60)
            print("INTELLIGENT CORRESPONDENCE ASSISTANT - CYCLIC MODE")
            print("=" * 60)
            print(
                f"Cycle Interval: {cycle_interval} seconds ({cycle_interval/60:.1f} minutes)"
            )
            print("Press Ctrl+C to stop")
            print("=" * 60 + "\n")

            try:
                while True:
                    run_email_processing_cycle(agent)
                    print(f"⏳ Waiting {cycle_interval} seconds until next cycle...")
                    time.sleep(cycle_interval)
            except KeyboardInterrupt:
                print("\n\n✓ Agent stopped by user")
        else:
            # Single run mode
            print("\n" + "=" * 60)
            print("INTELLIGENT CORRESPONDENCE ASSISTANT - SINGLE RUN")
            print("=" * 60 + "\n")
            run_email_processing_cycle(agent)

    except Exception as exc:
        print(f"An error occurred while running the agent: {exc}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
