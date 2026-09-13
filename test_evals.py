import json
import pytest
from run_evals import run_eval_case

with open("eval_cases.json") as f:
    CASES = json.load(f)


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_eval_case(case):
    result = run_eval_case(case)
    assert result["passed"], f"Failed: {case['question']} -> {result['answer'][:300]}"
