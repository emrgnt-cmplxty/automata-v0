"""Module for the completion provider"""
import os
from enum import Enum

from agent.constants import (
    ADVANCED_SYSTEM_PROMPT,
    AGENT_INSTRUCTIONS,
)
from automata.agent import OpenAIAutomataAgent
from automata.config import OpenAIAutomataAgentConfigBuilder
from automata.llm import OpenAIChatCompletionProvider, OpenAIConversation
from automata.singletons.dependency_factory import dependency_factory
from automata.singletons.py_module_loader import py_module_loader
from automata.tools.agent_tool_factory import AgentToolFactory
from automata.symbol import SymbolGraph

from utils import get_root_fpath


class RunMode(Enum):
    """Specifies the mode of running the completion provider"""

    VANILLA_ZERO_SHOT = "vanilla-zero-shot"
    ADVANCED_AGENT = "advanced-agent-with-py-interpreter"


class CompletionProvider:
    """Concrete class for completion providers"""

    def __init__(
        self,
        run_mode: RunMode,
        model: str,
        temperature: float,
    ):
        self.run_mode = run_mode
        self.model = model
        self.temperature = temperature
        self.completion_instance = OpenAIChatCompletionProvider(
            model=self.model,
            temperature=self.temperature,
            stream=True,
            conversation=OpenAIConversation(),
            functions=[],
        )

    def get_completion(self, **kwargs) -> str:
        """Returns the raw and cleaned completions for the given prompt"""
        vanilla_instructions = self.get_formatted_instruction(**kwargs)
        return self.generate_vanilla_completion(
            vanilla_instructions,
        )

    def generate_vanilla_completion(self, instructions: str) -> str:
        """Generates a vanilla completion for the given prompt"""
        if self.run_mode == RunMode.VANILLA_ZERO_SHOT:
            return self.completion_instance.standalone_call(instructions)
        elif self.run_mode == RunMode.ADVANCED_AGENT:
            return self.advanced_agent_factory(instructions).run()

    def advanced_agent_factory(self, instructions: str) -> OpenAIAutomataAgent:
        """Generates an advanced agent instance."""
        automata_path = os.path.join(get_root_fpath(), "automata")
        if not py_module_loader.initialized:
            py_module_loader.initialize(root_fpath="")
        symbol_graph = SymbolGraph(
            os.path.join(
                automata_path,
                "automata-embedding-data",
                "indices",
                "automata.scip",
            )
        )
        dependency_factory.set_overrides(symbol_graph=symbol_graph)
        toolkits = ["py-interpreter"]
        tool_dependencies = dependency_factory.build_dependencies_for_tools(
            toolkits
        )
        tools = AgentToolFactory.build_tools(toolkits, **tool_dependencies)

        config_builder = (
            OpenAIAutomataAgentConfigBuilder()
            .with_stream(True)
            .with_verbose(True)
            .with_tools(tools)  # type: ignore
            .with_system_template(ADVANCED_SYSTEM_PROMPT)
            .with_model(self.model)
            .with_temperature(self.temperature)
        )
        return OpenAIAutomataAgent(instructions, config_builder.build())

    def get_formatted_instruction(
        self, task_input: str, code_snippet: str
    ) -> str:
        """Formats the instruction for the given prompt"""

        return AGENT_INSTRUCTIONS.format(
            TASK_PROMPT=task_input, CODE_PROMPT=code_snippet
        )
