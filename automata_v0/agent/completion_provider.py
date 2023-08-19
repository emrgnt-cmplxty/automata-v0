"""Module for the completion provider"""
import textwrap
from enum import Enum
from typing import List, Optional, Tuple

from agent.constants import (
    ADVANCED_SYSTEM_PROMPT,
    AGENT_INSTRUCTIONS,
)

from automata.agent import OpenAIAutomataAgent
from automata.config import OpenAIAutomataAgentConfigBuilder
from automata.llm import OpenAIChatCompletionProvider, OpenAIConversation
from automata.singletons.dependency_factory import dependency_factory
from automata.tools import Tool
from automata.tools.agent_tool_factory import AgentToolFactory


class RunMode(Enum):
    """Specifies the mode of running the completion provider"""

    VANILLA = "vanilla"
    VANILLA_AGENT_WITH_INTERPRETER = "vanilla-agent-with-interpreter"
    ADVANCED_AGENT_WITH_INTERPRETER_AND_ORACLE = (
        "vanilla-agent-with-interpreter-and-oracle"
    )


class CompletionProvider:
    """Concrete class for completion providers"""

    def __init__(self, run_mode: RunMode, model: str, temperature: float):
        self.run_mode = run_mode
        self.model = model
        self.temperature = temperature

    def get_raw_and_cleaned_completions(
        self, task: str, code: str, additional_tools=[]
    ) -> Tuple[str, str]:
        """Returns the raw and cleaned completions for the given prompt"""
        if self.run_mode == RunMode.VANILLA:
            vanilla_instructions = self.get_formatted_instruction(task, code)
            raw_completion = self.generate_vanilla_completion(
                vanilla_instructions
            )
        else:
            vanilla_system_prompt = self.get_system_prompt()
            vanilla_instructions = self.get_formatted_instruction(task, code)
            tools = []
            if self.run_mode == RunMode.VANILLA_AGENT_WITH_INTERPRETER:
                toolkits = ["py-interpreter"]

                tool_dependencies = (
                    dependency_factory.build_dependencies_for_tools(toolkits)
                )
                tools = AgentToolFactory.build_tools(
                    toolkits, **tool_dependencies
                )
            tools += additional_tools
            raw_completion = self.generate_agent_completion(
                vanilla_system_prompt, vanilla_instructions, tools
            )
        clean_completion = self.extract_code(raw_completion)
        return (raw_completion, clean_completion)

    def generate_vanilla_completion(self, instructions: str) -> str:
        """Generates a vanilla completion for the given prompt"""
        provider = OpenAIChatCompletionProvider(
            model=self.model,
            temperature=self.temperature,
            stream=True,
            conversation=OpenAIConversation(),
            functions=[],
        )
        return provider.standalone_call(instructions)

    def generate_agent_completion(
        self,
        system_prompt: str,
        instructions: str,
        tools: Optional[List[Tool]] = None,
    ) -> str:
        """Generates an agent completion for the given prompt"""
        if not tools:
            tools = []

        config_builder = (
            OpenAIAutomataAgentConfigBuilder()
            .with_stream(True)
            .with_verbose(True)
            .with_tools(tools)  # type: ignore
            .with_system_template(system_prompt)
            .with_model(self.model)
            .with_temperature(self.temperature)
        )

        agent = OpenAIAutomataAgent(instructions, config_builder.build())

        try:
            return agent.run()
        except Exception as e:
            return f"Exception {e} occurred while running."

    def extract_code(self, raw_completion: str) -> str:
        """Extracts the markdown snippet from the raw completion"""
        # Extract the markdown snippet for results like '```python ...```'
        # or '```....```'
        clean_completion = (
            raw_completion.split("```python")[1].split("```")[0]
            if "```python" in raw_completion
            else raw_completion
        )
        clean_completion = (
            clean_completion.split("```")[1].split("```")[0]
            if "```" in clean_completion
            else clean_completion
        )
        clean_completion = clean_completion.replace("\\n", "\n")
        return clean_completion

    def get_system_prompt(self) -> str:
        """Returns the system prompt for the given run mode"""
        if self.run_mode == RunMode.VANILLA:
            raise ValueError("Vanilla mode does not have a system prompt")
        elif self.run_mode == RunMode.ADVANCED_AGENT_WITH_INTERPRETER:
            return ADVANCED_SYSTEM_PROMPT

    def get_formatted_instruction(
        self, task_prompt: str, code_prompt: str
    ) -> str:
        """Formats the instruction for the given prompt"""

        return AGENT_INSTRUCTIONS.format(
            TASK_PROMPT=task_prompt, CODE_PROMPT=code_prompt
        )
