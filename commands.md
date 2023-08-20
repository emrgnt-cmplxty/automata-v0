# Commands used

## Setup

```bash

git submodule update --init --recursive


cd automata_v0/leetcode_hard_gym 
cd ../../

poetry update

poetry install
```

## LeetCode-Hard

## HumanEval Evaluations

### Evaluate automata results on HumanEval

```bash
poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/human_eval_model_eq_gpt_4_0613_temp_eq_0p7_run_mode_eq_vanilla.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5
# Base
# {'pass@1': 0.8170731707317073}
# Base + Extra
# {'pass@1': 0.7560975609756098}

poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/human_eval_model_eq_gpt_4_0613_temp_eq_0p7_run_mode_eq_advanced_agent_with_interpreter.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5
# Base
# {'pass@1': 0.8170731707317073}
# Base + Extra
# {'pass@1': 0.7439024390243902}
```

### Evaluate reflexion results on HumanEval

```bash
cd automata_v0/reflexion/programming_runs

python main.py --run_name "test_reflexion" --root_dir "root" --dataset_path ./benchmarks/humaneval-py.jsonl --strategy "reflexion" --language "py" --model "gpt-4-0613" --pass_at_k "1" --max_iters "2" --verbose

cp root/simple_leetcode_python3_gpt4_visible/leetcode-hard-py-40-uncontaminated_tests._simple_1_gpt-4-0613_pass_at_k_1_py.jsonl ../../data/results/leetcode_results/gpt_4_0613/leetcode-hard-py-40-uncontaminated_tests._simple_1_gpt-4-0613_pass_at_k_1_py.jsonl

cd -

poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/humaneval-py._reflexion_5_gpt-4_pass_at_k_1_py.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5
# Base
# {'pass@1': 0.725609756097561}
# Base + Extra
# {'pass@1': 0.6524390243902439}
```

### Generate and evaluate automata results on LeetCode-Hard

```bash

poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0301
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0613

poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-4-0314
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-4-0613


poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0314
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0613

poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=advanced-agent-with-py-interpreter --model=gpt-4-0314
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=advanced-agent-with-py-interpreter --model=gpt-4-0613
```

### Generate and evaluate reflexion results on LeetCode-Hard

```bash
cd automata_v0/reflexion/programming_runs

# simple gpt-4-0314
python main.py --run_name "simple_leetcode_python3_gpt4_visible" --root_dir "root" --dataset_path ./executors/leetcode_env/leetcode_dataset/data/humaneval/leetcode-hard-py-40-uncontaminated_tests.jsonl --strategy "simple" --language "py" --model "gpt-4-0314" --pass_at_k "1" --max_iters "1" --is_leetcode --verbose

# simple gpt-4-0613
python main.py --run_name "simple_leetcode_python3_gpt4_visible" --root_dir "root" --dataset_path ./executors/leetcode_env/leetcode_dataset/data/humaneval/leetcode-hard-py-40-uncontaminated_tests.jsonl --strategy "simple" --language "py" --model "gpt-4-0613" --pass_at_k "1" --max_iters "1" --is_leetcode --verbose


# reflexion gpt-4-0314
python main.py --run_name "reflexion_leetcode_python3_gpt4_react_constraints_visible" --root_dir "root" --dataset_path ./executors/leetcode_env/leetcode_dataset/data/humaneval/leetcode-hard-py-40-uncontaminated_tests.jsonl --strategy "reflexion" --language "py" --model "gpt-4-0314" --pass_at_k "1" --max_iters "5" --is_leetcode --verbose

# reflexion gpt-4-0613
python main.py --run_name "reflexion_leetcode_python3_gpt4_react_constraints_visible" --root_dir "root" --dataset_path ./executors/leetcode_env/leetcode_dataset/data/humaneval/leetcode-hard-py-40-uncontaminated_tests.jsonl --strategy "reflexion" --language "py" --model "gpt-4-0613" --pass_at_k "1" --max_iters "5" --is_leetcode --verbose

cd -
```
