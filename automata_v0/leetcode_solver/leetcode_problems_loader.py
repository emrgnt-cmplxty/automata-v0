import os
import textwrap
from typing import Any, Tuple
from utils import get_root_fpath, clean_html_content
import pandas as pd

"""An implementation for loading leetcode problems from the gym"""


class LeetCodeLoader:
    """Concrete class responsible for loading and providing LeetCode problems."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.data = pd.read_csv(self.data_path)
        self.data_full = pd.read_csv(
            os.path.join(
                get_root_fpath(),
                "data",
                "inputs",
                "leetcode_full.csv",
            )
        )

    def get_problem_header(self, idx: int) -> str:
        """Retrieve a problem by its index."""
        row = self.data.iloc[idx]
        return f"Title:{row['question_title']}\n\nDescription:\n{row['description']}"

    def get_problem_context(self, idx: int) -> str:
        """Retrieve a problem by its index."""
        row = self.data.iloc[idx]
        raw_content = self.data_full[
            self.data_full["question_id"] == row["question_id"]
        ]["raw_content"].iloc[0]
        return f"LeetCode Problem #{row['frontend_question_id']}\nTitle: {row['question_title']}\nDescription:\n{clean_html_content(raw_content)}\n\n"

    def get_problem_id_slug(self, idx: int) -> Tuple[int, int, Any]:
        """Retrieve a problem by its index."""
        row = self.data.iloc[idx]
        return (
            int(row["frontend_question_id"]),  # type: ignore
            int(row["question_id"]),  # type: ignore
            row["question_slug"],
        )

    def get_problem_slug(self, idx: int) -> Any:
        """Get the backend problem id for a given problem."""
        row = self.data.iloc[idx]
        return str(row["question_slug"])  # type: ignore

    def get_backend_problem_id(self, idx: int) -> int:
        """Get the backend problem id for a given problem."""
        row = self.data.iloc[idx]
        return int(row["question_id"])  # type: ignore

    def get_frontend_problem_id(self, idx: int) -> int:
        """Get the frontend problem id for a given problem."""
        row = self.data.iloc[idx]
        return int(row["frontend_question_id"])  # type: ignore

    def get_snippet(self, idx: int) -> int:
        """Get the frontend problem id for a given problem."""
        row = self.data.iloc[idx]
        return row["python3_snippet"]  # type: ignore
