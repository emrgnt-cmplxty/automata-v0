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
