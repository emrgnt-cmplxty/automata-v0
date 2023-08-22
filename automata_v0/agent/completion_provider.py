"""Module for the completion provider"""
from enum import Enum

from agent.constants import (
    ADVANCED_SYSTEM_PROMPT,
    AGENT_CODING_INSTRUCTIONS,
    AGENT_MATH_INSTRUCTIONS,
)
from automata.agent import OpenAIAutomataAgent
from automata.config import OpenAIAutomataAgentConfig
from automata.experimental.tools import PyInterpreterOpenAIToolkitBuilder
from automata.llm import OpenAIChatCompletionProvider, OpenAIConversation


class RunMode(Enum):
    """Specifies the mode of running the completion provider"""

    VANILLA_ZERO_SHOT = "vanilla-zero-shot"
    ADVANCED_AGENT = "advanced-agent-with-py-interpreter"


class ProblemType(Enum):
    """Specifies the type of problem"""

    LEETCODE = "leetcode"
    HUMANEVAL = "humaneval"
    MATH = "math"


class CompletionProvider:
    """Concrete class for completion providers"""

    def __init__(
        self,
        run_mode: RunMode,
        model: str,
        temperature: float,
        problem_type: ProblemType = ProblemType("leetcode"),
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
        self.problem_type = problem_type

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
        else:
            return self.advanced_agent_factory(instructions).run()

    def advanced_agent_factory(self, instructions: str) -> OpenAIAutomataAgent:
        """Generates an advanced agent instance."""
        tools = PyInterpreterOpenAIToolkitBuilder().build_for_open_ai()
        config = OpenAIAutomataAgentConfig(
            stream=True,
            verbose=True,
            tools=tools,
            system_instruction=ADVANCED_SYSTEM_PROMPT,
            model=self.model,
            temperature=self.temperature,
        )
        return OpenAIAutomataAgent(instructions, config)

    def get_formatted_instruction(
        self, task_input: str, code_snippet: str
    ) -> str:
        """Formats the instruction for the given prompt"""
        if (
            self.problem_type == ProblemType.LEETCODE
            or self.problem_type == ProblemType.HUMANEVAL
        ):
            return AGENT_CODING_INSTRUCTIONS.format(
                TASK_PROMPT=task_input, CODE_PROMPT=code_snippet
            )
        elif self.problem_type == ProblemType.MATH:
            return AGENT_MATH_INSTRUCTIONS.format(TASK_PROMPT=task_input)
