# automata-v0

## Install

```bash
git submodule update --init --recursive

cd automata_v0/leetcode_hard_gym && poetry update && poetry install && cd ../../ 
cd automata_v0/automata && poetry update && poetry install && cd ../../ 
cd automata_v0/reflexion && poetry update && poetry install && cd ../../ 

poetry update && poetry install
```

## Environment Variables

```bash
echo OPENAI_API_KEY_LOCAL=your_openai_key\\nLEETCODE_SESSION=your_leet_code_session > .env
```

## Minimal Reproduction -

### Vanilla LeetCode-Hard

```bash
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-4-0613

# >>> expect to see 1-2 out of 40 correct
```

### Automata LeetCode-Hard

```bash
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=advanced-agent-with-py-interpreter --model=gpt-4-0613

# >>> expect to see 3-4 out of 40 correct
```

### Vanilla HumanEval

```bash
poetry run python automata_v0/run_human_eval_solver.py --run_mode=vanilla-zero-shot --model=gpt-4-0613

poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/gpt_4_0613/human_eval_model_eq_gpt_4_0613_temp_eq_0p7_run_mode_eq_vanilla_zero_shot_solutions.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5

# Base
# {'pass@1': 0.8170731707317073}
# Base + Extra
# {'pass@1': 0.75}
```

### Automata HumanEval

```bash
poetry run python automata_v0/run_human_eval_solver.py --run_mode=advanced-agent-with-py-interpreter --model=gpt-4-0613

poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/gpt_4_0613/human_eval_model_eq_gpt_4_0613_temp_eq_0p7_run_mode_eq_vanilla.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5

# Base
# {'pass@1': 0.8170731707317073}
# Base + Extra
# {'pass@1': 0.7560975609756098}
```

## Extensive Reproduction -

Check the [commands.md](commands.md) file for more details.
