"""
01. 개별 메트릭 단독 사용하기
============================
RAGAS의 각 메트릭을 하나씩 실행해보면서 동작 원리를 이해합니다.
"""

import asyncio

from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextRecall,
    FactualCorrectness,
)
from llm_config import get_llm, get_embeddings

# ── Ollama (로컬 LLM) 설정 ────────────────────────────────
evaluator_llm = get_llm()
evaluator_embeddings = get_embeddings()


# ── 샘플 데이터 ───────────────────────────────────────────
# RAG 시스템이 "파이썬 GIL"에 대한 질문에 답한 상황을 시뮬레이션합니다.

sample_good = {
    "user_input": "파이썬의 GIL이란 무엇인가요?",
    "response": (
        "GIL(Global Interpreter Lock)은 CPython에서 한 번에 하나의 스레드만 "
        "파이썬 바이트코드를 실행할 수 있도록 하는 뮤텍스입니다. "
        "이로 인해 CPU 바운드 멀티스레딩의 성능이 제한됩니다."
    ),
    "retrieved_contexts": [
        "CPython의 GIL(Global Interpreter Lock)은 한 번에 하나의 스레드만 "
        "파이썬 바이트코드를 실행하도록 보장하는 뮤텍스이다. "
        "GIL은 메모리 관리를 단순화하지만, CPU 바운드 멀티스레드 프로그램의 "
        "성능을 제한하는 주요 원인이 된다.",
    ],
    "reference": (
        "GIL은 CPython의 Global Interpreter Lock으로, "
        "한 번에 하나의 스레드만 파이썬 바이트코드를 실행하게 제한하는 메커니즘이다."
    ),
}

# 환각이 포함된 나쁜 예시
sample_bad = {
    "user_input": "파이썬의 GIL이란 무엇인가요?",
    "response": (
        "GIL은 파이썬 3.13에서 완전히 제거되었으며, "  # ← 환각 (사실이 아님)
        "이제 파이썬은 완벽한 멀티스레딩을 지원합니다. "
        "또한 GIL은 자바에서 영감을 받아 만들어졌습니다."  # ← 환각
    ),
    "retrieved_contexts": [
        "CPython의 GIL(Global Interpreter Lock)은 한 번에 하나의 스레드만 "
        "파이썬 바이트코드를 실행하도록 보장하는 뮤텍스이다.",
    ],
    "reference": (
        "GIL은 CPython의 Global Interpreter Lock으로, "
        "한 번에 하나의 스레드만 파이썬 바이트코드를 실행하게 제한하는 메커니즘이다."
    ),
}


# ── 각 메트릭별 ascore 호출 ────────────────────────────────
# 메트릭마다 필요한 인자가 다릅니다:
#   Faithfulness:      user_input, response, retrieved_contexts
#   AnswerRelevancy:   user_input, response
#   ContextRecall:     user_input, retrieved_contexts, reference
#   FactualCorrectness: response, reference

METRIC_ARGS = {
    "Faithfulness": lambda s: dict(
        user_input=s["user_input"], response=s["response"], retrieved_contexts=s["retrieved_contexts"]
    ),
    "AnswerRelevancy": lambda s: dict(
        user_input=s["user_input"], response=s["response"]
    ),
    "ContextRecall": lambda s: dict(
        user_input=s["user_input"], retrieved_contexts=s["retrieved_contexts"], reference=s["reference"]
    ),
    "FactualCorrectness": lambda s: dict(
        response=s["response"], reference=s["reference"]
    ),
}


async def evaluate_single_metric(metric, sample, label: str):
    """하나의 메트릭으로 하나의 샘플을 평가합니다."""
    name = metric.__class__.__name__
    args = METRIC_ARGS[name](sample)
    result = await metric.ascore(**args)
    score = float(result)
    print(f"  {name:25s} = {score:.4f}  ({label})")
    return score


async def main():
    print("=" * 60)
    print("RAGAS 개별 메트릭 테스트")
    print("=" * 60)

    metrics = [
        Faithfulness(llm=evaluator_llm),
        AnswerRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings),
        ContextRecall(llm=evaluator_llm),
        FactualCorrectness(llm=evaluator_llm),
    ]

    # ── 좋은 답변 평가 ──
    print("\n✅ 좋은 답변 (context에 충실한 응답)")
    for metric in metrics:
        await evaluate_single_metric(metric, sample_good, "good")

    # ── 나쁜 답변 평가 ──
    print("\n❌ 나쁜 답변 (환각이 포함된 응답)")
    for metric in metrics:
        await evaluate_single_metric(metric, sample_bad, "bad")

    print("\n" + "=" * 60)
    print("해석 가이드:")
    print("  - Faithfulness: 높을수록 context에 충실 (환각 없음)")
    print("  - AnswerRelevancy: 높을수록 질문에 적절한 답변")
    print("  - ContextRecall: 높을수록 context가 정답을 잘 포함")
    print("  - FactualCorrectness: 높을수록 사실적으로 정확")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
