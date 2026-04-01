"""
RAGAS 학습 프로젝트
===================
RAG 파이프라인 평가를 위한 RAGAS 프레임워크 학습용 코드입니다.

실행 순서:
  1. python 01_single_metric.py   — 개별 메트릭 이해
  2. python 02_full_evaluation.py  — 전체 평가 파이프라인
  3. python 03_testset_generation.py — 합성 테스트 데이터 생성

사전 준비:
  1. uv sync (또는 pip install -e .)
  2. .env 파일에 OPENAI_API_KEY 설정
"""

import subprocess
import sys


def main():
    scripts = {
        "1": ("01_single_metric.py", "개별 메트릭 단독 사용"),
        "2": ("02_full_evaluation.py", "전체 평가 파이프라인"),
        "3": ("03_testset_generation.py", "합성 테스트 데이터 생성"),
    }

    print("RAGAS 학습 프로젝트")
    print("=" * 40)
    for key, (script, desc) in scripts.items():
        print(f"  {key}. {desc} ({script})")
    print("  q. 종료")
    print()

    choice = input("실행할 예제를 선택하세요: ").strip()
    if choice in scripts:
        script, _ = scripts[choice]
        subprocess.run([sys.executable, script])
    elif choice == "q":
        print("종료합니다.")
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
