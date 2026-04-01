# RAGAS 학습 프로젝트

RAGAS(Retrieval Augmented Generation Assessment)는 RAG 파이프라인을 평가하기 위한 프레임워크입니다.

## 설치

```bash
# 의존성 설치 (uv 사용)
uv sync

# 또는 pip
pip install -e .

# OpenAI API 키 설정
cp .env.example .env
# .env 파일에 실제 API 키 입력
```

## 프로젝트 구조

```
├── main.py                    # 기본 RAG 평가 예제
├── 01_single_metric.py        # 개별 메트릭 단독 사용
├── 02_full_evaluation.py      # 전체 메트릭 평가
├── 03_testset_generation.py   # 합성 테스트 데이터 생성
└── docs/                      # 테스트 데이터 생성용 샘플 문서
```

## RAGAS 핵심 개념

### 평가 대상 4가지 축

| 축 | 메트릭 | 측정 대상 |
|---|---|---|
| **Retrieval 품질** | Context Precision | 검색된 문서 중 관련 문서의 비율과 순위 |
| **Retrieval 완전성** | Context Recall (LLMContextRecall) | 정답을 뒷받침하는 정보가 검색 결과에 포함되었는지 |
| **Generation 충실성** | Faithfulness | 생성된 답변이 검색된 컨텍스트에 근거하는지 (환각 탐지) |
| **Generation 적절성** | Response Relevancy | 생성된 답변이 질문에 적절한지 |

### 메트릭 상세

#### 1. Faithfulness (충실성)

**비교 대상:** `response` vs `retrieved_contexts`
**핵심 질문:** "LLM이 검색된 문서에 근거해서 답변했는가? 지어낸 건 없는가?"

측정 과정:
```
Step 1: response에서 개별 claim(주장)을 추출
        "GIL은 뮤텍스이다" → claim 1
        "한 번에 하나의 스레드만 실행" → claim 2
        "CPU 바운드 성능이 제한된다" → claim 3

Step 2: 각 claim이 retrieved_contexts에 의해 뒷받침되는지 판정
        claim 1 → context에 있음 ✅
        claim 2 → context에 있음 ✅
        claim 3 → context에 있음 ✅

Step 3: 점수 = 뒷받침되는 claim 수 / 전체 claim 수
        = 3/3 = 1.0
```

환각이 포함된 답변의 경우:
```
        "3.13에서 완전히 제거" → context에 없음 ❌
        "완벽한 멀티스레딩 지원" → context에 없음 ❌
        "자바에서 영감"        → context에 없음 ❌

        점수 = 0/3 = 0.0  ← 환각 탐지!
```

**용도:** 환각(hallucination) 탐지. 이 점수가 낮으면 LLM이 context에 없는 내용을 지어낸 것.

#### 2. ResponseRelevancy (응답 적절성)

**비교 대상:** `response` → (역생성된 질문들) vs `user_input`
**핵심 질문:** "답변이 질문에 대해 적절한 내용인가? 쓸데없는 말이 많지 않은가?"

측정 과정:
```
Step 1: response로부터 질문을 역으로 생성 (N개)
        response: "GIL은 CPython의 뮤텍스로..."
        → 역생성 질문 1: "GIL이란 무엇인가?"
        → 역생성 질문 2: "CPython의 동시성 제한은?"
        → 역생성 질문 3: "GIL의 역할은?"

Step 2: 역생성된 질문들과 원래 질문의 임베딩을 비교 (코사인 유사도)
        "파이썬의 GIL이란?" ↔ "GIL이란 무엇인가?"       → 유사도 0.95
        "파이썬의 GIL이란?" ↔ "CPython의 동시성 제한은?" → 유사도 0.60
        "파이썬의 GIL이란?" ↔ "GIL의 역할은?"           → 유사도 0.72

Step 3: 점수 = 평균 코사인 유사도
        = (0.95 + 0.60 + 0.72) / 3 ≈ 0.76
```

- 답변에 질문과 무관한 내용이 많으면 → 역생성 질문이 원래 질문과 달라짐 → 점수 하락
- 답변이 정확히 질문에 맞는 내용이면 → 역생성 질문이 원래 질문과 유사 → 점수 상승
- 이 메트릭만 **임베딩 모델이 필요** (코사인 유사도 계산)

#### 3. LLMContextRecall (컨텍스트 재현율)

**비교 대상:** `reference` vs `retrieved_contexts`
**핵심 질문:** "검색기가 정답을 뒷받침하는 문서를 충분히 가져왔는가?"

측정 과정:
```
Step 1: reference(정답)를 문장 단위로 분해
        "GIL은 CPython의 Global Interpreter Lock이다" → 문장 1
        "한 번에 하나의 스레드만 실행하게 제한한다"       → 문장 2

Step 2: 각 문장이 retrieved_contexts에 의해 뒷받침되는지 판정
        문장 1 → context에 있음 ✅
        문장 2 → context에 있음 ✅

Step 3: 점수 = 뒷받침되는 문장 수 / 전체 문장 수
        = 2/2 = 1.0
```

- 이 메트릭은 **Retriever(검색기)의 성능**만 평가
- response(LLM 답변)는 전혀 보지 않음
- **reference(모범답안)가 필수**
- 점수가 낮다면 → 검색기가 관련 문서를 못 찾고 있음 → 검색 전략 개선 필요

#### 4. FactualCorrectness (사실 정확도)

**비교 대상:** `response` vs `reference`
**핵심 질문:** "LLM 답변이 모범답안과 비교해서 사실적으로 맞는가?"

측정 과정:
```
Step 1: response에서 claim 추출
        claim A: "GIL은 뮤텍스이다"
        claim B: "한 번에 하나의 스레드만 실행"

Step 2: reference에서 claim 추출
        claim X: "GIL은 Global Interpreter Lock이다"
        claim Y: "한 번에 하나의 스레드만 실행하게 제한"

Step 3: 각 claim을 교차 비교
        TP (True Positive):  response claim이 reference와 일치
        FP (False Positive): response claim이 reference에 없음 (오류)
        FN (False Negative): reference claim이 response에 없음 (누락)

Step 4: F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

Faithfulness와의 차이:
- **Faithfulness:** response vs retrieved_contexts → "context에 근거했나?"
- **FactualCorrectness:** response vs reference → "정답과 비교해서 맞나?"

Faithfulness가 높아도 FactualCorrectness가 낮을 수 있음.
예) 검색된 문서 자체가 틀린 정보 → LLM은 context에 충실(Faithfulness ↑), 하지만 정답과 불일치(FactualCorrectness ↓)

### 메트릭 비교 요약

```
메트릭               비교 대상                    평가 대상      핵심 질문
──────────────────────────────────────────────────────────────────────────
Faithfulness         response ↔ contexts         Generator     환각이 있는가?
ResponseRelevancy    response ↔ user_input       Generator     질문에 맞는 답인가?
LLMContextRecall     reference ↔ contexts        Retriever     문서를 잘 찾았는가?
FactualCorrectness   response ↔ reference        Generator     사실적으로 정확한가?
```

- **Retriever 개선이 필요한 경우:** LLMContextRecall이 낮음
- **Generator 개선이 필요한 경우:** Faithfulness, ResponseRelevancy, FactualCorrectness가 낮음
- **검색은 잘 되는데 답변이 이상한 경우:** Context Recall은 높지만 Faithfulness가 낮음 → 프롬프트 튜닝 필요

### 데이터 구조

RAGAS 평가에 필요한 데이터 필드:

| 필드 | 설명 | 필요한 메트릭 |
|---|---|---|
| `user_input` | 사용자 질문 | 전부 |
| `response` | RAG가 생성한 답변 | Faithfulness, Relevancy, Factual Correctness |
| `retrieved_contexts` | 검색된 문서 리스트 | Faithfulness, Context Precision/Recall |
| `reference` | 정답 (ground truth) | Context Recall, Factual Correctness |

### LLM 설정

RAGAS v0.4의 `llm_factory()`는 내부적으로 **instructor** 라이브러리를 사용합니다.
instructor가 다양한 LLM 프로바이더를 지원하므로, OpenAI뿐 아니라 Claude, Gemini 등도 사용할 수 있습니다.

#### 프로바이더별 설정 예시

```python
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from ragas.llms import llm_factory

# OpenAI
llm = llm_factory("gpt-4o-mini")

# Anthropic Claude
llm = llm_factory("claude-sonnet-4-20250514", client=AsyncAnthropic())

# Google Gemini (LiteLLM 경유)
llm = llm_factory("gemini/gemini-2.0-flash")

# Ollama (OpenAI 호환 API)
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
llm = llm_factory("qwen2.5:latest", client=client)
```

| 프로바이더 | 패키지 | 환경변수 |
|---|---|---|
| OpenAI | `openai` (기본 포함) | `OPENAI_API_KEY` |
| Claude | `anthropic` | `ANTHROPIC_API_KEY` |
| Gemini | `litellm` | `GEMINI_API_KEY` |
| Ollama | `openai` (호환 API) | 불필요 (로컬) |

> **참고:** 임베딩은 OpenAI 호환 API만 지원합니다.
> Claude/Gemini를 LLM으로 사용하더라도 임베딩은 OpenAI 또는 Ollama(nomic-embed-text)를 사용합니다.

#### 이 프로젝트의 설정 (Ollama 로컬 환경)

`ollama_config.py`에 공통 설정이 정의되어 있습니다:

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings

# Ollama는 OpenAI 호환 API를 제공
ollama_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# LLM (평가/생성용)
evaluator_llm = llm_factory("qwen2.5:latest", client=ollama_client)

# Embedding (ResponseRelevancy 메트릭에서 코사인 유사도 계산에 사용)
evaluator_embeddings = OllamaEmbeddings(client=ollama_client, model="nomic-embed-text")
```
