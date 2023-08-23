"""Load and process math problems and solutions."""
import argparse
import json
import logging
import os
import numpy as np
from glob import glob
from utils import parse_arguments
from agent.completion_provider import CompletionProvider, RunMode, ProblemType
import openai
import dotenv
import pandas as pd
from evalplus.data import write_jsonl
from automata_v0.utils import get_root_fpath
from math_helpers.math_equivalence import is_equiv
from automata_v0.utils import (
    load_existing_jsonl,
)

# Constants
MATH_RESULTS_FILE_NAME = "math_results_{MODEL}_{TEMPERATURE}_{RUN_MODE}.jsonl"
MATH_RESULTS_DIR = os.path.join(
    get_root_fpath(), "data", "results", "math_results"
)
NUM_SAMPLES_DEFAULT = 250
INPUTS = glob(os.path.join("data", "inputs", "MATH", "*", "*"))

dotenv.load_dotenv()
np.random.seed(42)


def load_existing_problems(output_path: str):
    existing_data = load_existing_jsonl(output_path)
    return existing_data, {entry["problem"] for entry in existing_data}


def load_inputs(existing_problems=None):
    indices = list(range(len(INPUTS)))
    np.random.shuffle(indices)

    results = []
    for index in indices:
        with open(INPUTS[index], "r") as f:
            problem_data = json.loads(f.read())
            if (
                existing_problems
                and problem_data["problem"] in existing_problems
            ):
                continue  # Skip problems that have already been observed
            results.append(problem_data)

    return pd.DataFrame(results)


def configure_paths(args: argparse.Namespace) -> None:
    """Configure paths for the run."""
    args.solutions_output_data_dir = (
        args.solutions_output_data_dir or MATH_RESULTS_DIR
    )
    args.solutions_output_file_name = (
        args.solutions_output_file_name
        or MATH_RESULTS_FILE_NAME.format(
            MODEL=args.model,
            TEMPERATURE=args.temperature,
            RUN_MODE=args.run_mode,
        )
    )


def remove_boxed(s):
    left = "oxed{"
    try:
        assert s[: len(left)] == left
        assert s[-1] == "}"
        return s[len(left) : -1]
    except:
        return None


def last_boxed_only_string(string):
    idx = string.rfind("oxed{")
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx == None:
        retval = None
    else:
        retval = string[idx : right_brace_idx + 1]

    return retval


def process_problems_solutions(args: argparse.Namespace):
    openai.api_key = os.getenv("OPENAI_API_KEY_LOCAL", "")

    solutions_output_path = os.path.join(
        args.solutions_output_data_dir, args.solutions_output_file_name
    )
    results, existing_problems = load_existing_problems(solutions_output_path)
    # print("results = ", results)
    rewards = 0
    for counter, result in enumerate(results):
        print(result)

        answer = remove_boxed(last_boxed_only_string(result["solution"]))
        attempt = remove_boxed(last_boxed_only_string(result["completion"]))
        print(f"answer={answer}, attempt={attempt}")

        is_equivalent = is_equiv(answer, attempt) or is_equiv(
            answer, attempt[::-1] if attempt else ""
        )
        rewards += float(is_equivalent)
        print(f"is_equiv={is_equivalent}")
        print(f"acc={rewards/(counter+1)}")
        print(f"counter={counter}")
        # break
    # for i_sample in range(num_samples):
    #     try:
    #         problem, solution = df.problem[i_sample], df.solution[i_sample]
    #         if problem in existing_problems:
    #             continue

    #         print(f"\nProblem:\n{problem}")
    #         print(f"\nSolution:\n{solution}")

    #         completion_provider = CompletionProvider(
    #             run_mode=RunMode(args.run_mode),
    #             model=args.model,
    #             temperature=args.temperature,
    #             problem_type=ProblemType("math"),
    #         )

    #         completion = completion_provider.get_completion(
    #             task_input=problem, code_snippet=None
    #         )
    #         print(f"\nCompletion:\n{completion}")

    #         results.append(
    #             {
    #                 "problem": problem,
    #                 "solution": solution,
    #                 "completion": completion,
    #             }
    #         )
    #         if not os.path.exists(args.solutions_output_data_dir):
    #             os.makedirs(args.solutions_output_data_dir, exist_ok=True)
    #         write_jsonl(solutions_output_path, results)

    #     except Exception as e:
    #         print(f"Exception: {e}")


def main():
    # Parse arguments
    args = parse_arguments()
    configure_paths(
        args,
    )
    process_problems_solutions(args)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    main()
