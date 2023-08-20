"""Study the dataset."""
import argparse
import logging
import os
import time
from typing import Tuple

from evalplus.data import write_jsonl
from leetcode_hard_gym.leetcode_env.environment import LeetCodeEnv
from leetcode_hard_gym.leetcode_env.leetcode_types import (
    LeetCodeSubmission,
    ProgrammingLanguage,
)
from utils import extract_code, parse_arguments

from automata_v0.utils import (
    get_configured_logger,
    get_root_fpath,
    load_existing_jsonl,
)

LEETCODE_SOLUTIONS_FILE_NAME = "leetcode_hard_py_40__model_eq_{MODEL}__temp_eq_{TEMPERATURE}__run_mode_eq_{RUN_MODE}.jsonl"
LEETCODE_SOLUTIONS_DIR = os.path.join(
    get_root_fpath(), "data", "results", "leetcode_results", "{MODEL}"
)


def load_existing_task_ids(existing_data: list[dict]) -> set[str]:
    """Load existing task ids from the data."""
    return {entry["task_id"] for entry in existing_data}


def configure_paths(args: argparse.Namespace) -> None:
    """Configure paths for the run."""
    args.problems_data_path = args.problems_data_path


def load_data(args: argparse.Namespace) -> Tuple[list[dict], set[str]]:
    """Load existing data."""
    existing_data = load_existing_jsonl(args.output_path)

    existing_task_ids = (
        set() if args.overwrite else load_existing_task_ids(existing_data)
    )

    completion_seqs = existing_data or []

    return existing_task_ids, completion_seqs


def main(logger: logging.Logger):
    # Parse arguments
    args = parse_arguments()
    configure_paths(args)

    results = load_existing_jsonl(args.problems_data_path)
    env = LeetCodeEnv()

    completion_seqs = []

    rewards = {}
    reward_sum = 0
    for count, result in enumerate(results):
        logger.info("result = ", result)
        try:
            clean_completion = extract_code(result["raw_completion"])
        except Exception as e:
            clean_completion = ""

        logger.info(f"clean_completion = {clean_completion}")

        status, reward, done, submission_result = env.step(
            LeetCodeSubmission(
                code=clean_completion,
                lang=ProgrammingLanguage.PYTHON3,
                question_id=result["problem_id"],
                question_slug=result["problem_slug"],
                timeout=12,
            )
        )
        logger.info(f"status={status}, reward={reward}, done={done}")
        logger.info(f"submission_result = {submission_result}")

        outpath = args.problems_data_path.replace(".jsonl", "_fixed.jsonl")

        completion_seqs.append(
            {
                "task_id": result["task_id"],
                "completion": result["completion"],
                "raw_completion": result["raw_completion"],
                "status": status,
                "reward": reward,
                "done": done,
                "submission_result": submission_result,
                "problem_slug": result["problem_slug"],
                "problem_id": result["problem_id"],
                "frontend_problem_id": result["frontend_problem_id"],
            }
        )

        rewards[result["problem_slug"]] = reward
        reward_sum += int(reward)
        logger.info(f"rewards = {rewards}")
        logger.info(f"reward_sum / count = {reward_sum} / {(count+1)}")
        write_jsonl(outpath, completion_seqs)
        time.sleep(5)


if __name__ == "__main__":
    logger = get_configured_logger(__name__, "INFO")
    main(logger)
