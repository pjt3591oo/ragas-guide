"""
03. 합성 테스트 데이터셋 생성
==============================
문서로부터 자동으로 질문-답변 쌍을 생성합니다.
수동으로 평가 데이터를 만들 필요 없이 RAG 시스템을 테스트할 수 있습니다.
"""

import os

from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from ragas.testset import TestsetGenerator
from llm_config import get_llm, get_embeddings

# ── Ollama (로컬 LLM) 설정 ────────────────────────────────
generator_llm = get_llm()
generator_embeddings = get_embeddings()

# ── 문서 로드 ─────────────────────────────────────────────
# docs/ 디렉토리의 마크다운 파일들을 로드합니다.
loader = DirectoryLoader(
    "docs/",
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)
documents = loader.load()
print(f"📄 로드된 문서 수: {len(documents)}")
for doc in documents:
    print(f"   - {doc.metadata.get('source', 'unknown')} ({len(doc.page_content)} chars)")


def main():
    print("=" * 60)
    print("RAGAS 합성 테스트 데이터셋 생성")
    print("=" * 60)

    # ── TestsetGenerator 생성 ──
    generator = TestsetGenerator(
        llm=generator_llm,
        embedding_model=generator_embeddings,
    )

    # ── 테스트셋 생성 ──
    # testset_size: 생성할 질문-답변 쌍의 수
    print("\n🔄 테스트 데이터 생성 중... (1-2분 소요)")
    testset = generator.generate_with_langchain_docs(
        documents=documents,
        testset_size=5,  # 학습용이므로 적게 생성
    )

    # ── 결과 확인 ──
    df = testset.to_pandas()
    print(f"\n✅ {len(df)}개의 테스트 샘플이 생성되었습니다.\n")

    for i, row in df.iterrows():
        print(f"--- 샘플 {i + 1} ---")
        print(f"  질문: {row.get('user_input', 'N/A')}")
        response = row.get("reference", "N/A")
        if isinstance(response, str) and len(response) > 100:
            response = response[:100] + "..."
        print(f"  참조 답변: {response}")
        print()

    # ── CSV로 저장 ──
    output_path = "generated_testset.csv"
    df.to_csv(output_path, index=False)
    print(f"💾 테스트셋이 {output_path}에 저장되었습니다.")
    print("   이 데이터를 사용하여 RAG 시스템을 평가할 수 있습니다.")


if __name__ == "__main__":
    main()
