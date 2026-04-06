# REST API 설계 가이드

## REST API란

REST(Representational State Transfer)는 웹 서비스를 설계하기 위한 아키텍처 스타일입니다.
HTTP 프로토콜을 기반으로 클라이언트와 서버 간의 통신 규약을 정의합니다.

REST API는 자원(Resource)을 URI로 식별하고, HTTP 메서드로 자원에 대한
행위를 표현합니다. 상태를 서버에 저장하지 않는 무상태(Stateless) 특성이 핵심입니다.

## HTTP 메서드

REST API에서 자원에 대한 CRUD(Create, Read, Update, Delete) 작업은
HTTP 메서드로 매핑됩니다.

주요 메서드:
- GET: 자원 조회. 서버의 상태를 변경하지 않음 (안전, 멱등)
- POST: 새 자원 생성. 요청마다 새로운 자원이 생성됨 (비멱등)
- PUT: 자원 전체 교체. 같은 요청을 여러 번 보내도 결과가 동일 (멱등)
- PATCH: 자원 일부 수정. 변경할 필드만 전송
- DELETE: 자원 삭제. 이미 삭제된 자원에 다시 요청하면 404 (멱등)

멱등성(Idempotency)은 같은 요청을 여러 번 보내도 결과가 동일한 성질입니다.
GET, PUT, DELETE는 멱등이고, POST는 멱등이 아닙니다.
네트워크 오류로 재시도가 필요한 경우 멱등성이 중요합니다.

## URI 설계 원칙

좋은 URI 설계는 API의 가독성과 사용성에 직접적인 영향을 미칩니다.

설계 원칙:
- 자원은 명사로 표현: /users, /articles, /orders
- 복수형 사용: /user가 아닌 /users
- 계층 관계 표현: /users/{id}/orders (특정 사용자의 주문 목록)
- 동사 사용 금지: /getUsers 대신 GET /users
- 소문자 사용: /Users가 아닌 /users
- 하이픈(-) 사용: /user-profiles (언더스코어 대신)

잘못된 예시와 올바른 예시:
- 잘못됨: GET /getUser?id=1 → 올바름: GET /users/1
- 잘못됨: POST /deleteUser → 올바름: DELETE /users/1
- 잘못됨: POST /updateUser → 올바름: PUT /users/1

## 상태 코드

HTTP 상태 코드는 요청 처리 결과를 클라이언트에게 알려줍니다.

2xx (성공):
- 200 OK: 요청 성공 (일반적인 성공 응답)
- 201 Created: 자원 생성 성공 (POST 요청의 성공)
- 204 No Content: 성공했지만 응답 본문 없음 (DELETE 성공 시)

3xx (리다이렉션):
- 301 Moved Permanently: 자원이 영구적으로 이동
- 304 Not Modified: 캐시된 버전 사용 가능

4xx (클라이언트 오류):
- 400 Bad Request: 잘못된 요청 (유효성 검증 실패)
- 401 Unauthorized: 인증 필요 (로그인 안 됨)
- 403 Forbidden: 권한 없음 (인증됐지만 접근 불가)
- 404 Not Found: 자원이 존재하지 않음
- 409 Conflict: 충돌 (중복 생성 등)
- 422 Unprocessable Entity: 문법은 맞지만 처리 불가
- 429 Too Many Requests: 요청 횟수 초과 (Rate Limiting)

5xx (서버 오류):
- 500 Internal Server Error: 서버 내부 오류
- 502 Bad Gateway: 게이트웨이/프록시 오류
- 503 Service Unavailable: 서비스 일시 중단

## 페이지네이션

대량의 데이터를 한 번에 반환하면 성능 문제가 발생합니다.
페이지네이션을 통해 데이터를 나누어 전달합니다.

오프셋 기반 페이지네이션:
- GET /users?page=2&per_page=20
- 장점: 구현이 단순, 특정 페이지로 바로 이동 가능
- 단점: 데이터 추가/삭제 시 항목이 누락되거나 중복될 수 있음

커서 기반 페이지네이션:
- GET /users?cursor=eyJpZCI6MTAwfQ&limit=20
- 장점: 실시간 데이터에서도 안정적, 대규모 데이터에 효율적
- 단점: 특정 페이지로 바로 이동 불가

응답에는 메타 정보를 포함하는 것이 좋습니다:
- total: 전체 항목 수
- page / cursor: 현재 위치
- next / previous: 다음/이전 페이지 링크

## 인증과 보안

API 보안을 위한 주요 인증 방식:

API Key:
- 간단한 인증 방식으로 헤더나 쿼리 파라미터로 전달
- 서버 간 통신에 적합하지만 단독으로는 보안이 약함

OAuth 2.0:
- 제3자 애플리케이션에 제한된 접근 권한을 부여
- Authorization Code, Client Credentials 등 여러 흐름 지원
- 소셜 로그인, 외부 API 연동에 널리 사용

JWT (JSON Web Token):
- 자체적으로 정보를 담고 있는 토큰 (self-contained)
- Header.Payload.Signature 구조
- 서버에 세션을 저장하지 않아 확장성이 좋음
- 토큰 만료 시간 설정 필수, Refresh Token과 함께 사용

보안 모범 사례:
- HTTPS 필수 사용
- Rate Limiting으로 남용 방지
- 입력 유효성 검증 (SQL Injection, XSS 방지)
- 민감한 데이터는 응답에서 제외
- CORS(Cross-Origin Resource Sharing) 적절히 설정

## API 버전 관리

API는 변경이 불가피하므로 버전 관리가 필요합니다.

URI 경로 방식:
- /api/v1/users, /api/v2/users
- 장점: 직관적이고 명확
- 단점: URI가 변경됨

헤더 방식:
- Accept: application/vnd.api+json;version=2
- 장점: URI가 깔끔하게 유지
- 단점: 테스트와 디버깅이 어려움

쿼리 파라미터 방식:
- /api/users?version=2
- 장점: 쉬운 전환
- 단점: 캐싱 문제 발생 가능

일반적으로 URI 경로 방식이 가장 널리 사용됩니다.
주요 변경(breaking change) 시에만 버전을 올리고,
하위 호환이 유지되는 변경은 같은 버전 내에서 처리합니다.

## 에러 처리

일관된 에러 응답 형식은 API 사용자 경험에 중요합니다.

권장 에러 응답 구조:
- error.code: 머신이 읽을 수 있는 에러 코드
- error.message: 사람이 읽을 수 있는 에러 메시지
- error.details: 상세 정보 (유효성 검증 실패 필드 등)

에러 처리 원칙:
- 일관된 형식으로 에러를 반환
- 보안에 민감한 내부 오류 메시지는 노출하지 않음
- 클라이언트가 문제를 해결할 수 있도록 충분한 정보 제공
- 적절한 HTTP 상태 코드 사용
