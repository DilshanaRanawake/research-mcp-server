import json
from server import search_papers


def run_eval_case(case: dict) -> dict:
    answer = search_papers(case["question"])
    answer_lower = answer.lower()

    passed_keywords = all(kw.lower() in answer_lower for kw in case.get("expected_keywords", []))
    failed_on_forbidden = any(bad.lower() in answer_lower for bad in case.get("must_not_contain", []))

    return {
        "id": case["id"],
        "passed": passed_keywords and not failed_on_forbidden,
        "answer": answer,
    }


def run_all():
    with open("eval_cases.json") as f:
        cases = json.load(f)

    results = [run_eval_case(c) for c in cases]
    passed = sum(r["passed"] for r in results)

    print(f"{passed}/{len(results)} eval cases passed\n")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['id']}")
        if not r["passed"]:
            print(f"        -> {r['answer'][:200]}")

    return results


if __name__ == "__main__":
    run_all()
