from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from pydantic import BaseModel

from src.engine.decision import ActionType
from src.memory.models import AgentState
from src.memory.state_manager import update_state_from_tool
from src.skills.base import SkillName
from src.tools.hello_world import HelloWorldClient
from src.tools.executor import ToolExecutor
from src.tools.models import ToolName

from src.engine import LLMExecutor, AgentActionCoordinator
from src.llm import LLMCallError
from src.logger import get_agent_logger
from src.memory import (
    create_initial_state,
    update_state_from_skill,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AgentConfig:
    """Runtime configuration for the agent."""

    iteration_step_limit: int = 100


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Return value from a full agent run."""

    state: AgentState
    steps_executed: int

    def summary(self) -> str:
        # dump memory
        return f"Agent completed with state: {self.state}"


class Agent:
    """High-level entry point that hides coordinator/LLM/tool orchestration."""

    def __init__(
        self,
        *,
        llm_executor: LLMExecutor,
        hello_world_client: HelloWorldClient,
        tool_executor: ToolExecutor,
        config: Optional[AgentConfig] = None,
        coordinator: Optional[AgentActionCoordinator] = None,
    ) -> None:
        self._llm_executor = llm_executor
        self._hello_world_client = hello_world_client
        self._tool_executor = tool_executor
        self._config = config or AgentConfig()
        self._coordinator = coordinator or AgentActionCoordinator()
        self._logger = get_agent_logger()

    @classmethod
    def from_env(
        cls,
        *,
        agent_config: Optional[AgentConfig] = None,
    ) -> "Agent":
        """Create an agent wired to environment-configured dependencies."""

        llm_executor = LLMExecutor.from_env()
        hello_world_client = HelloWorldClient()
        tool_executor = ToolExecutor.from_env()
        return cls(
            llm_executor=llm_executor,
            hello_world_client=hello_world_client,
            tool_executor=tool_executor,
            config=agent_config,
        )

    def run(
        self,
        goal: str,
    ) -> AgentResult:
        """Execute the research workflow for the given topic."""

        state = create_initial_state(goal=goal)
        steps_executed = 0
        for step in range(self._config.iteration_step_limit):
            steps_executed = step + 1
            decision = self._coordinator.next_action(state)

            if decision.action_type == ActionType.COMPLETE:
                break
            if decision.action_type == ActionType.NOOP:
                break

            if decision.action_type == ActionType.LLM_SKILL and decision.skill:
                self._logger.info(f"Invoking LLM skill: {decision.skill.value}")
                context = self._build_prompt_context(state)
                output = self._llm_call(decision.skill, context)
                self._logger.info(f"LLM Skill Output: {output}")
                state = update_state_from_skill(state, decision.skill, output)
                continue

            if decision.action_type == ActionType.TOOL and decision.tool_type:
                self._logger.info(f"Executing tool: {decision.tool_type.value}")
                output = self._execute_tool(state, decision.tool_type)
                self._logger.info(f"Tool Output: {output}")
                state = update_state_from_tool(state, decision.tool_type, output)
                continue

            raise RuntimeError(f"Unhandled coordinator decision: {decision}")
        else:
            # Only executed if the for-loop does not break
            message = (
                "Reached step limit before completion. Consider increasing max_steps."
            )
            logger.warning(message)
            self._logger.warning(message)

        return AgentResult(state=state, steps_executed=steps_executed)

    def _build_prompt_context(self, state: AgentState) -> Dict[str, object]:
        """Build context for LLM prompt rendering."""
        context = {
            "state": state,
            "core": state.core,
            "semantic": state.semantic,
            "episodic": state.episodic,
            "workflow": state.workflow,
            "working": state.working,
            "procedural": state.procedural,
            "resource": state.resource,
        }

        # Add email-specific context if in email analysis stage
        if state.workflow.current_stage.value == "ANALYZE_EMAIL":
            # Load email content if not already loaded
            if not state.working.email_processing.current_file_content:
                current_file = state.working.email_processing.get_current_file()
                if current_file:
                    from src.tools.models import ReadEmailRequest
                    from src.tools.email_tools import read_email

                    request = ReadEmailRequest(file_path=current_file)
                    email_response = read_email(request)
                    context["email_content"] = email_response.content
                    context["file_name"] = email_response.file_name
                else:
                    context["email_content"] = ""
                    context["file_name"] = ""
            else:
                current_file = state.working.email_processing.get_current_file()
                context["email_content"] = (
                    state.working.email_processing.current_file_content
                )
                context["file_name"] = (
                    current_file.split("/")[-1] if current_file else ""
                )

        return context

    def _llm_call(self, skill_name: SkillName, context: Dict[str, object]) -> BaseModel:
        try:
            return self._llm_executor.execute(skill_name, context)
        except LLMCallError as exc:
            raise RuntimeError(
                f"LLM call failed for {skill_name.value}: {exc}"
            ) from exc

    def _execute_tool(self, state: AgentState, tool_type: ToolName) -> BaseModel:
        return self._tool_executor.execute(tool_type, state)
