# automata-v0

## Install

```bash
git submodule update --init --recursive

poetry install
```

## Run

``bash
echo OPENAI_API_KEY_LOCAL=$OPENAI_API_KEY_LOCAL\\nLEETCODE_SESSION=$LEETCODE_SESSION > .env
poetry run python automata_v0/run_vanilla_problem_solver.py
```
