"""
02. 전체 평가 파이프라인
========================
여러 샘플을 한 번에 평가하고 결과를 DataFrame으로 확인합니다.
실제 RAG 시스템을 평가하는 전형적인 워크플로우입니다.
"""

import os

from dotenv import load_dotenv

load_dotenv()

from ragas import evaluate, EvaluationDataset
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextRecall,
    FactualCorrectness,
)
from llm_config import get_llm, get_embeddings

# ── Ollama (로컬 LLM) 설정 ────────────────────────────────
evaluator_llm = get_llm()
evaluator_embeddings = get_embeddings()

# ── 평가 데이터셋 ─────────────────────────────────────────
# 실제로는 RAG 시스템의 출력을 수집하여 이 형태로 구성합니다.
eval_data = [
    {
        "user_input": "파이썬의 GIL이란 무엇인가요?",
        "response": (
            "GIL(Global Interpreter Lock)은 CPython에서 한 번에 하나의 스레드만 "
            "파이썬 바이트코드를 실행할 수 있도록 하는 뮤텍스입니다."
        ),
        "retrieved_contexts": [
            "CPython의 GIL은 한 번에 하나의 스레드만 파이썬 바이트코드를 "
            "실행하도록 보장하는 뮤텍스이다. GIL은 메모리 관리를 단순화하지만 "
            "CPU 바운드 멀티스레드 프로그램의 성능을 제한한다.",
        ],
        "reference": "GIL은 CPython의 뮤텍스로, 한 번에 하나의 스레드만 바이트코드를 실행하게 한다.",
    },
    {
        "user_input": "리스트 컴프리헨션과 for 루프의 차이점은?",
        "response": (
            "리스트 컴프리헨션은 for 루프보다 간결하고 일반적으로 더 빠릅니다. "
            "내부적으로 C 레벨에서 최적화되어 있기 때문입니다."
        ),
        "retrieved_contexts": [
            "리스트 컴프리헨션은 기존 리스트로부터 새로운 리스트를 만드는 간결한 방법이다. "
            "일반적인 for 루프보다 성능이 좋은데, 이는 내부적으로 C 코드로 최적화되어 있기 때문이다.",
            "for 루프는 반복 가능한 객체의 각 요소에 대해 코드 블록을 실행하는 제어 구조이다.",
        ],
        "reference": "리스트 컴프리헨션은 for 루프보다 간결하고, C 레벨 최적화로 인해 더 빠르다.",
    },
    {
        "user_input": "파이썬에서 데코레이터란?",
        "response": (
            "데코레이터는 자바에서 가져온 기능으로, "  # ← 부분적으로 부정확
            "함수에 추가 기능을 붙이는 문법입니다. "
            "@기호를 사용하며, 성능을 3배 향상시킵니다."  # ← 환각
        ),
        "retrieved_contexts": [
            "파이썬 데코레이터는 다른 함수를 인자로 받아 기능을 확장하는 함수이다. "
            "@기호를 사용하여 적용하며, 로깅, 인증, 캐싱 등에 활용된다.",
        ],
        "reference": (
            "데코레이터는 다른 함수를 감싸서 기능을 확장하는 파이썬의 문법으로, "
            "@기호를 사용하여 적용한다."
        ),
    },
    {
        "user_input": "async/await는 언제 사용하나요?",
        "response": (
            "async/await는 I/O 바운드 작업에서 비동기 처리를 위해 사용합니다. "
            "네트워크 요청이나 파일 읽기 등에서 대기 시간을 효율적으로 활용할 수 있습니다."
        ),
        "retrieved_contexts": [
            "파이썬의 async/await 구문은 비동기 I/O를 위한 것이다. "
            "네트워크 통신, 파일 I/O 등 대기가 필요한 작업에서 이벤트 루프를 통해 "
            "효율적으로 여러 작업을 동시에 처리할 수 있다.",
        ],
        "reference": (
            "async/await는 I/O 바운드 비동기 작업에 사용되며, "
            "이벤트 루프를 통해 동시성을 구현한다."
        ),
    },
]

dataset = EvaluationDataset.from_list(eval_data)


def main():
    print("=" * 60)
    print("RAGAS 전체 평가 파이프라인")
    print("=" * 60)

    result = evaluate(
        dataset=dataset,
        metrics=[
            Faithfulness(),
            ResponseRelevancy(),
            LLMContextRecall(),
            FactualCorrectness(),
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    # ── 전체 점수 요약 ──
    print("\n📊 전체 평균 점수:")
    print(result)

    # ── 샘플별 상세 결과 ──
    df = result.to_pandas()
    print("\n📋 샘플별 상세 결과:")
    metric_cols = [c for c in df.columns if c not in ("user_input", "retrieved_contexts", "response", "reference")]
    print(df[["user_input"] + metric_cols].to_string(index=False))

    # ── 문제 있는 샘플 식별 ──
    print("\n⚠️  Faithfulness < 0.5인 샘플 (환각 의심):")
    low_faith = df[df["faithfulness"] < 0.5]
    if low_faith.empty:
        print("  없음 — 모든 답변이 context에 충실합니다.")
    else:
        for _, row in low_faith.iterrows():
            print(f"  - Q: {row['user_input']}")
            print(f"    Faithfulness: {row['faithfulness']:.2f}")

    # ── CSV로 저장 ──
    output_path = "evaluation_results.csv"
    df.to_csv(output_path, index=False)
    print(f"\n💾 결과가 {output_path}에 저장되었습니다.")


if __name__ == "__main__":
    main()
