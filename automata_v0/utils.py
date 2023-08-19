import json
import logging
import os


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
