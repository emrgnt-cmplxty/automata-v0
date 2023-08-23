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
np.random.seed(43)


def load_existing_problems(output_path: str):
    existing_data = load_existing_jsonl(output_path)
    return existing_data, {entry["problem"] for entry in existing_data}


def load_inputs(num_events=10, existing_problems=None):
    indices = list(range(len(INPUTS)))
    np.random.shuffle(indices)

    results = []
    for index in indices[:num_events]:
        with open(INPUTS[index], "r") as f:
            problem_data = json.loads(f.read())
            if (
                existing_problems
                and problem_data["problem"] in existing_problems
            ):
                continue  # Skip problems that have already been observed
            results.append(problem_data)

    return pd.DataFrame(results)


def configure_paths(args: argparse.Namespace, num_samples: int) -> None:
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


def process_problems_solutions(args: argparse.Namespace, num_events: int):
    df = load_inputs(num_events)
    openai.api_key = os.getenv("OPENAI_API_KEY_LOCAL", "")

    solutions_output_path = os.path.join(
        args.solutions_output_data_dir, args.solutions_output_file_name
    )
    results, existing_problems = load_existing_problems(solutions_output_path)

    for i_sample in range(num_events):
        try:
            problem, solution, level, ptype = (
                df.problem[i_sample],
                df.solution[i_sample],
                df.level[i_sample],
                df.type[i_sample],
            )

            if level != "Level 5":
                continue

            if problem in existing_problems:
                continue

            print(f"\nProblem:\n{problem}")
            print(f"\nSolution:\n{solution}")

            completion_provider = CompletionProvider(
                run_mode=RunMode(args.run_mode),
                model=args.model,
                temperature=args.temperature,
                problem_type=ProblemType("math"),
            )

            completion = completion_provider.get_completion(
                task_input=problem, code_snippet=None
            )
            print(f"\nCompletion:\n{completion}")

            results.append(
                {
                    "problem": problem,
                    "type": ptype,
                    "level": level,
                    "solution": solution,
                    "completion": completion,
                }
            )
            if not os.path.exists(args.solutions_output_data_dir):
                os.makedirs(args.solutions_output_data_dir, exist_ok=True)
            write_jsonl(solutions_output_path, results)

        except Exception as e:
            print(f"Exception: {e}")


def main():
    # Parse arguments
    args = parse_arguments()
    num_events = args.num_events or NUM_SAMPLES_DEFAULT
    configure_paths(args, num_events)
    process_problems_solutions(args, num_events)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    main()


# import pandas as pd
# import json
# import os
# import numpy as np
# from glob import glob
# from utils import parse_arguments
# from agent.completion_provider import CompletionProvider, RunMode, ProblemType
# import openai
# import dotenv
# from evalplus.data import write_jsonl


# from automata_v0.utils import (
#     get_root_fpath,
# )

# dotenv.load_dotenv()

# np.random.seed(42)


# def load(num_events=10):
#     inputs = glob(os.path.join("data", "inputs", "MATH", "*", "*"))
#     print(f"len(inputs) = {len(inputs)}")
#     indices = list(range(len(inputs)))
#     np.random.shuffle(indices)

#     results = []
#     for index in indices[:num_events]:
#         with open(inputs[index], "r") as f:
#             results.append(json.loads(f.read()))

#     return pd.DataFrame(results)


# if __name__ == "__main__":
#     args = parse_arguments()

#     n_samples = 250
#     df = load(n_samples)

#     openai.api_key = os.getenv("OPENAI_API_KEY_LOCAL", "")

#     args.solutions_output_data_dir = (
#         args.solutions_output_data_dir
#         or os.path.join(get_root_fpath(), "data", "results", "math_results")
#     )
#     args.solutions_output_file_name = (
#         args.solutions_output_file_name
#         or f"math_results_{args.model}_{args.temperature}_{args.run_mode}.jsonl"
#     )

#     solutions_output_path = os.path.join(
#         args.solutions_output_data_dir, args.solutions_output_file_name
#     )
#     results = []
#     for i_sample in range(n_samples):
#         problem, solution = df.problem[i_sample], df.solution[i_sample]

#         completion_provider = CompletionProvider(
#             run_mode=RunMode(args.run_mode),
#             model=args.model,
#             temperature=args.temperature,
#             problem_type=ProblemType("math"),
#         )

#         completion = completion_provider.get_completion(
#             task_input=problem, code_snippet=None
#         )
#         print(f"\nProblem:\n{problem}")
#         print(f"\nSolution:\n{solution}")
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
