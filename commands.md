# Commands used

```bash
git submodule update --init --recursive


cd automata_v0/leetcode_hard_gym 
cd ../../

poetry update

poetry install


# Generate results on LeetCode-Hard
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0301
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0613

poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-4-0314
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-4-0613


poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0314
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=vanilla-zero-shot --model=gpt-3.5-turbo-0613

poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=advanced-agent-with-py-interpreter --model=gpt-4-0314
poetry run python automata_v0/run_leetcode_hard_solver.py --run_mode=advanced-agent-with-py-interpreter --model=gpt-4-0613


# Human Eval Evaluations
poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/humaneval-py._reflexion_5_gpt-4_pass_at_k_1_py.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5
# Base
# {'pass@1': 0.725609756097561}
# Base + Extra
# {'pass@1': 0.6524390243902439}

poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/human_eval_model_eq_gpt-4-0613_temp_eq_0.7_run_mode_eq_vanilla.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5
# Base
# {'pass@1': 0.8170731707317073}
# Base + Extra
# {'pass@1': 0.7560975609756098}

poetry run evalplus.evaluate --dataset humaneval --samples=automata_v0/data/results/humaneval_results/human_eval_model_eq_gpt-4-0613_temp_eq_0.7_run_mode_eq_advanced-agent-with-interpreter.jsonl --parallel 4 --min-time-limit 0.5 --gt-time-limit-factor 5
# Base
# {'pass@1': 0.8170731707317073}
# Base + Extra
# {'pass@1': 0.7439024390243902}

```
