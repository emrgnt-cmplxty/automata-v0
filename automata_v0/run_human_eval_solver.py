"""Basic agency study, e.g. simple completion / agent generation"""
import argparse
import openai
import os
from tqdm import tqdm

from agent.completion_provider import CompletionProvider, RunMode
from evalplus.data import get_human_eval_plus, write_jsonl

from automata_v0.utils import (
    get_root_fpath,
    load_existing_jsonl,
)

from utils import parse_arguments, extract_code

HUMANEVAL_SOLUTIONS_FILE_NAME = "human_eval_model_eq_{MODEL}_temp_eq_{TEMPERATURE}_run_mode_eq_{RUN_MODE}_solutions.jsonl"
HUMANEVAL_SOLUTIONS_DIR = os.path.join(
    get_root_fpath(),
    "data",
    "results",
    "humaneval_results",
)


def load_existing_task_ids(existing_data):
    return {entry["task_id"] for entry in existing_data}


def main() -> None:
    """Main function for generating human eval solutions"""
    # Parse arguments
    args = parse_arguments()

    openai.api_key = os.getenv("OPENAI_API_KEY_LOCAL", "")

    if not RunMode(args.run_mode):
        raise ValueError(
            f"Invalid mode: {args.run_mode}, Available modes: {RunMode}"
        )

    completion_provider = CompletionProvider(
        run_mode=RunMode(args.run_mode),
        model=args.model,
        temperature=args.temperature,
    )
    problems = get_human_eval_plus()

    task_ids = sorted(problems.keys())
    prompts = [problems[task_id]["prompt"] for task_id in task_ids]
    num_samples = len(prompts)
    print(f"Number of samples: {num_samples}")

    output_dir = args.solutions_output_data_dir or HUMANEVAL_SOLUTIONS_DIR
    output_file_name = (
        args.solutions_output_file_name
        or HUMANEVAL_SOLUTIONS_FILE_NAME.format(
            MODEL=args.model,
            TEMPERATURE=args.temperature,
            RUN_MODE=args.run_mode,
        )
    )
    output_path = os.path.join(output_dir, output_file_name)

    existing_data = load_existing_jsonl(output_path)
    existing_task_ids = (
        set() if args.overwrite else load_existing_task_ids(existing_data)
    )

    completion_seqs = existing_data or []

    for i in tqdm(range(num_samples), ncols=0, total=num_samples):
        print(f"Loading sample i = {i}")

        task_id = task_ids[i]
        if task_id in existing_task_ids and not args.overwrite:
            print(
                f"Skipping task_id {task_id} as it already exists in the output file."
            )
            continue

        raw_prompt = prompts[i]
        print(f"Passing raw prompt ={raw_prompt}")

        raw_completion = completion_provider.get_completion(
            task_input=raw_prompt,
            code_snippet=raw_prompt,
        )
        clean_completion = extract_code(raw_completion)

        print(f"Found Raw Completion = {raw_completion}")

        completion_seqs.append(
            {
                "task_id": task_ids[i],
                "completion": clean_completion,
                "raw_completion": raw_completion,
            }
        )
        print(f"Writing output to {output_path}")
        write_jsonl(output_path, completion_seqs)


if __name__ == "__main__":
    main()
