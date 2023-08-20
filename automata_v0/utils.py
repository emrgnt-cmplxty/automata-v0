import argparse
import json
import logging
import os
import re

from bs4 import BeautifulSoup


def get_root_fpath() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_configured_logger(name: str, log_level: str) -> logging.Logger:
    log_level = getattr(logging, log_level.upper(), "INFO")
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(name)


def load_existing_jsonl(file_path: str) -> list[dict]:
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            return [json.loads(line) for line in json_file]
    return []


def extract_code(raw_response: str) -> str:
    def _extract_unformatted(raw_response):
        # Extract the class definition as before
        class_definition_match = re.search(
            r"class\s\S*:\s*.*?(?=\n\n|$)", raw_response, re.DOTALL
        )
        class_definition = (
            class_definition_match[0] if class_definition_match else None
        )

        # Find the position of the class definition in the raw_response
        class_position = (
            class_definition_match.start() if class_definition_match else -1
        )

        # Extract the lines before the class definition
        lines_before_class = raw_response[:class_position].strip().splitlines()

        # Extract the import statements by filtering lines that start with 'import' or 'from'
        import_statements = [
            line
            for line in lines_before_class
            if line.startswith(("import", "from"))
        ]

        # Combine the import statements and the class definition
        return "\n".join(import_statements + [class_definition])

    if "```python" in raw_response:
        cleaned_response = raw_response.split("```python")[1]
        return cleaned_response.split("```")[0]
    elif "```" in raw_response:
        cleaned_response = raw_response.split("```")[1]
        return cleaned_response.split("```")[0]
    else:
        return _extract_unformatted(raw_response)


def prep_for_leetcode(code: str) -> str:
    lines = code.split("\n")
    modified_lines = ["class Solution():"]
    for line in lines:
        if line.startswith("def "):
            line = "def " + line[4:].replace("(", "(self, ", 1)
        modified_lines.append(f"  {line}")
    return "\n".join(modified_lines)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Find similar solutions to LeetCode problems using OpenAI."
    )
    parser.add_argument(
        "--problems_data_path",
        default=None,
        help="Path to the LeetCode problems data.",
    )
    parser.add_argument(
        "--solutions_output_data_dir",
        default=None,
        help="Path to the solutions JSON file.",
    )
    parser.add_argument(
        "--solutions_output_file_name",
        default=None,
        help="Path to the solutions JSON file.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature parameter for OpenAI model.",
    )
    parser.add_argument(
        "--run_mode",
        type=str,
        default="vanilla-zero-shot",
        help="Run mode for the OpenAI model.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo-0613",
        help="Model name for OpenAI.",
    )
    parser.add_argument(
        "--overwrite",
        type=bool,
        default=False,
        help="Overwrite existing solutions.",
    )
    return parser.parse_args()


def clean_html_content(html_content: str) -> str:
    """Clean the HTML content of a LeetCode problem description"""
    if not isinstance(html_content, str):
        return html_content
    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Convert HTML to text with newline characters
    text_content = soup.get_text(separator="\n", strip=True)

    # Replace scientific notation numbers
    cleaned_content = re.sub(
        r"(\b10)\s+(\d+\b)", r"\1e\2", text_content
    )  # Replace "10 4" with "10e4"

    # Specific handling for power notation
    cleaned_content = re.sub(r"(\b\d+)\s+(\d+\b)", r"\1^\2", cleaned_content)

    # Spaces around operators
    cleaned_content = re.sub(r"(\s*<=\s*)", " <= ", cleaned_content)

    # Replace specific patterns with newline characters
    cleaned_content = cleaned_content.replace(
        " . ", ".\n"
    )  # Newline after periods

    # Specific handling for "O ( n 2 )" pattern
    cleaned_content = cleaned_content.replace("O ( n^2 )", "O(n^2)")

    # Replace unnecessary characters and whitespace
    cleaned_content = re.sub(
        r"\s+", " ", cleaned_content
    )  # Collapse multiple whitespace

    # Remove spaces after commas and before periods
    cleaned_content = re.sub(r"\s*,\s*", ", ", cleaned_content)
    cleaned_content = re.sub(r"\s*\.\s*", ". ", cleaned_content)

    # Specific handling for .length accessor
    cleaned_content = cleaned_content.replace(" . length", ".length")

    # Remove leading asterisks from problem numbers
    cleaned_content = re.sub(r"\*+(\d+)\.?", r"\1.", cleaned_content)

    # Remove trailing asterisks
    cleaned_content = re.sub(r"\*+$", "", cleaned_content)

    # Cleanup .length accessor
    cleaned_content = cleaned_content.replace(". length", ".length")
    # Cleanup leading asterisks (in case cmd above missfired)
    cleaned_content = cleaned_content.replace("***", "")
    # Cleanup period formatting for programmatic statements.
    cleaned_content = cleaned_content.replace("'. '", ".")

    return cleaned_content.strip()
