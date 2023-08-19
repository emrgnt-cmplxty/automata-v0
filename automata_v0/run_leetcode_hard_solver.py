# sourcery skip: avoid-global-variables, no-relative-imports, require-parameter-annotation, require-return-annotation
# flake8: noqa
"""Study the dataset."""
import argparse
import logging
import os
import openai
from typing import Tuple

from evalplus.data import write_jsonl
from leetcode_solver.leetcode_constants import (
    LEETCODE_PROBLEMS_PATH,
)
from leetcode_solver.leetcode_problems_loader import LeetCodeLoader
from leetcode_solver.leetcode_problem_solver import LeetCodeSolver
from automata_v0.utils import (
    get_root_fpath,
    get_configured_logger,
    load_existing_jsonl,
    prep_for_leetcode,
)


from leetcode_hard_gym.leetcode_env.environment import LeetCodeEnv
from leetcode_hard_gym.leetcode_env.types import (
    LeetCodeSubmission,
    ProgrammingLanguage,
)

from agent.completion_provider import CompletionProvider, RunMode

from utils import parse_arguments

logger = logging.getLogger(__name__)


LEETCODE_PROBLEMS_PATH = os.path.join(
    get_root_fpath(),
    "leetcode_hard_gym/leetcode_dataset/data/with_snippets/leetcode_hard_with_snippets_uncontaminated_tests.csv",
)
LEETCODE_SOLUTIONS_FILE_NAME = "leetcode_hard_py_40__model_eq_{MODEL}__temp_eq_{TEMPERATURE}__run_mode_eq_{RUN_MODE}.jsonl"
LEETCODE_SOLUTIONS_OUTPUT_DIR = os.path.join(
    get_root_fpath(), "data", "results", "leetcode_results", "{MODEL}"
)


def load_existing_task_ids(existing_data: list[dict]) -> set[str]:
    return {entry["task_id"] for entry in existing_data}


def configure_paths(args: argparse.Namespace) -> None:
    """Configure paths for the run."""
    args.problems_data_path = args.problems_data_path or LEETCODE_PROBLEMS_PATH
    args.solutions_output_data_dir = (
        args.solutions_output_data_dir
        or LEETCODE_SOLUTIONS_OUTPUT_DIR.format(
            MODEL=args.model.replace("-", "_").replace(".", "p")
        )
    )
    args.solutions_output_file_name = (
        args.solutions_output_file_name
        or LEETCODE_SOLUTIONS_FILE_NAME.format(
            MODEL=args.model.replace("-", "_").replace(".", "p"),
            TEMPERATURE=args.temperature,
            RUN_MODE=args.run_mode,
        )
    )
    args.output_path = os.path.join(
        args.solutions_output_data_dir, args.solutions_output_file_name
    )


def load_data(args: argparse.Namespace) -> Tuple[list[dict], set[str]]:
    existing_data = load_existing_jsonl(args.output_path)

    existing_task_ids = (
        set() if args.overwrite else load_existing_task_ids(existing_data)
    )

    completion_seqs = existing_data or []

    return existing_task_ids, completion_seqs


def get_tools(args: argparse.Namespace) -> list:
    # if (
    #     args.run_mode
    #     == RunMode.ADVANCED_AGENT_WITH_INTERPRETER_AND_ORACLE.value
    # ):
    #     solutions_finder = LeetCodeSolutionsFinder(
    #         OpenAIEmbeddingProvider(),
    #         max_entry_id=loader.get_frontend_problem_id(
    #             index
    #         ),  # Solutions are indexed along frontend problem id
    #         max_num_examples=1,
    #         num_examples_to_screen=25,
    #         solutions_data_path=LEETCODE_SOLUTIONS_PATH,
    #         lowest_difficulty="Medium",
    #     )
    #     tools = AgentifiedSolutionOracleOpenAIToolkitBuilder(
    #         leetcode_solution_finder=solutions_finder
    #     ).build_for_open_ai()  # type: ignore

    return []


def main(logger: logging.Logger):
    # Parse arguments
    args = parse_arguments()
    configure_paths(args)

    openai.api_key = os.getenv("OPENAI_API_KEY_LOCAL", "")

    logger.info(f"Loading problem data from {args.problems_data_path}")
    loader = LeetCodeLoader(args.problems_data_path)

    num_examples = len(loader.data)
    logger.info(f"Number of examples to run = {num_examples}")
    solver = LeetCodeSolver(num_examples)
    env = LeetCodeEnv()

    completion_provider = CompletionProvider(
        run_mode=RunMode(args.run_mode),
        model=args.model,
        temperature=args.temperature,
    )

    logger.info(f"Loading from {args.output_path}")
    if not os.path.exists(args.output_path):
        os.makedirs(os.path.dirname(args.output_path), exist_ok=True)

    existing_task_ids, completion_seqs = load_data(args)

    for index in solver.indices:
        task_id = f"LeetCode-Hard/{index}"

        if task_id in existing_task_ids and not args.overwrite:
            logger.info(
                f"Skipping task_id {task_id} as it already exists in the output file."
            )
            continue

        problem_context = loader.get_problem_context(index)
        print(
            f"Running w/ problem at index {index} and context:\n\n{problem_context}"
        )

        try:
            tools = get_tools()

            (
                raw_completion,
                clean_completion,
            ) = completion_provider.get_raw_and_cleaned_completions(
                problem_context, tools
            )

            status, reward, done, submission_result = env.step(
                LeetCodeSubmission(
                    code=prep_for_leetcode(clean_completion),
                    lang=ProgrammingLanguage.PYTHON3,
                    question_id=loader.get_backend_problem_id(index),
                    question_slug=loader.get_problem_slug(index),
                )
            )
            logger.info(
                f"status={status}, reward={reward}, done={done}, submission_result={submission_result}"
            )
            solver.log_result(index, reward)

            completion_seqs.append(
                {
                    "task_id": f"LeetCode-Hard/{index}",
                    "completion": clean_completion,
                    "raw_completion": raw_completion,
                    "status": status,
                    "reward": reward,
                    "done": done,
                    "submission_result": submission_result,
                    "problem_slug": loader.get_problem_slug(index),
                    "problem_id": loader.get_backend_problem_id(index),
                    "frontend_problem_id": loader.get_frontend_problem_id(
                        index
                    ),
                }
            )
            logger.info(f"Writing output to {args.output_path}")
            write_jsonl(args.output_path, completion_seqs)

        except Exception as e:
            logger.info(f"Failed with exception {e}")
            write_jsonl(args.output_path, completion_seqs)
            solver.log_result(index, False)


if __name__ == "__main__":
    logger = get_configured_logger(__name__, "DEBUG")
    main(logger)
