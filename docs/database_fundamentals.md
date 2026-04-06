# 데이터베이스 기초 가이드

## 데이터베이스란

데이터베이스(Database)는 구조화된 데이터를 효율적으로 저장, 검색, 관리하기 위한
시스템입니다. DBMS(Database Management System)는 데이터베이스를 관리하는
소프트웨어로, 데이터의 무결성, 동시성, 보안을 보장합니다.

데이터베이스는 크게 관계형(RDBMS)과 비관계형(NoSQL)으로 나뉩니다.
각각의 특성에 따라 적합한 사용 사례가 다르므로, 요구사항에 맞는 선택이 중요합니다.

## 관계형 데이터베이스 (RDBMS)

관계형 데이터베이스는 데이터를 테이블(행과 열) 형태로 저장하며,
테이블 간의 관계를 통해 데이터를 구조화합니다.

주요 RDBMS:
- PostgreSQL: 고급 기능이 풍부한 오픈소스 데이터베이스. JSON 지원, 확장성 우수
- MySQL: 가장 널리 사용되는 오픈소스 데이터베이스. 웹 애플리케이션에 최적화
- SQLite: 서버 없이 파일 기반으로 동작. 임베디드, 모바일 앱에 적합
- Oracle: 대규모 엔터프라이즈 환경에서 사용. 고가용성과 성능에 강점

관계형 데이터베이스의 핵심 개념:
- 테이블(Table): 행(row)과 열(column)로 구성된 데이터 저장 단위
- 기본키(Primary Key): 각 행을 고유하게 식별하는 열
- 외래키(Foreign Key): 다른 테이블과의 관계를 정의하는 열
- 인덱스(Index): 검색 성능을 향상시키는 자료 구조

## SQL 기초

SQL(Structured Query Language)은 관계형 데이터베이스를 조작하기 위한 표준 언어입니다.

주요 SQL 명령어 분류:
- DDL(Data Definition Language): CREATE, ALTER, DROP — 테이블 구조 정의
- DML(Data Manipulation Language): SELECT, INSERT, UPDATE, DELETE — 데이터 조작
- DCL(Data Control Language): GRANT, REVOKE — 접근 권한 관리
- TCL(Transaction Control Language): COMMIT, ROLLBACK — 트랜잭션 제어

자주 사용되는 SQL 패턴:
- JOIN: 여러 테이블의 데이터를 결합. INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN
- GROUP BY: 데이터를 그룹화하여 집계 함수(COUNT, SUM, AVG 등) 적용
- 서브쿼리: 쿼리 안에 중첩된 쿼리로 복잡한 조건 처리
- WINDOW 함수: ROW_NUMBER, RANK, LAG 등으로 행 간 계산 수행

## 정규화 (Normalization)

정규화는 데이터 중복을 최소화하고 무결성을 보장하기 위해 테이블을 분해하는 과정입니다.

정규형 단계:
- 제1정규형(1NF): 모든 열의 값이 원자적(atomic)이어야 함. 반복 그룹 제거
- 제2정규형(2NF): 1NF를 만족하고, 부분 종속 제거 (기본키 전체에 종속)
- 제3정규형(3NF): 2NF를 만족하고, 이행 종속 제거 (비키 속성 간 종속 제거)
- BCNF: 모든 결정자가 후보키인 경우

과도한 정규화는 조인 연산을 증가시켜 성능을 저하시킬 수 있습니다.
실무에서는 3NF 수준까지 정규화한 후, 성능을 위해 필요한 부분만
반정규화(denormalization)하는 것이 일반적입니다.

## 트랜잭션과 ACID

트랜잭션(Transaction)은 하나의 논리적 작업 단위로, 모두 성공하거나 모두 실패해야 합니다.
ACID 속성은 트랜잭션의 안정성을 보장합니다.

- Atomicity(원자성): 트랜잭션의 모든 연산이 완전히 수행되거나 전혀 수행되지 않음
- Consistency(일관성): 트랜잭션 전후로 데이터베이스가 일관된 상태를 유지
- Isolation(격리성): 동시에 실행되는 트랜잭션이 서로 간섭하지 않음
- Durability(지속성): 커밋된 트랜잭션의 결과는 영구적으로 저장

격리 수준(Isolation Level):
- READ UNCOMMITTED: 커밋되지 않은 데이터도 읽을 수 있음 (Dirty Read 가능)
- READ COMMITTED: 커밋된 데이터만 읽음 (대부분의 DBMS 기본값)
- REPEATABLE READ: 같은 트랜잭션 내에서 같은 쿼리는 같은 결과 반환
- SERIALIZABLE: 가장 높은 격리 수준. 트랜잭션이 순차적으로 실행되는 것처럼 동작

격리 수준이 높을수록 데이터 일관성은 보장되지만 동시성 성능은 떨어집니다.

## NoSQL 데이터베이스

NoSQL(Not Only SQL)은 관계형 모델과 다른 방식으로 데이터를 저장합니다.

유형별 특징:
- 문서형(Document): MongoDB, CouchDB — JSON 형태의 문서로 저장. 스키마 유연
- 키-값형(Key-Value): Redis, DynamoDB — 단순한 키-값 쌍. 캐싱에 최적
- 열 기반(Column-Family): Cassandra, HBase — 대규모 분산 데이터 처리
- 그래프형(Graph): Neo4j, ArangoDB — 노드와 엣지로 관계 표현. 소셜 네트워크에 적합

NoSQL을 선택하는 상황:
- 스키마가 자주 변경되는 경우
- 수평 확장(scale-out)이 필요한 대규모 시스템
- 비정형 또는 반정형 데이터를 다루는 경우
- 읽기/쓰기 성능이 극도로 중요한 경우

## 인덱스와 성능 최적화

인덱스는 데이터 검색 속도를 높이는 자료 구조로, B-Tree, Hash, GiST 등의
구조가 사용됩니다.

인덱스 설계 원칙:
- WHERE 절에 자주 사용되는 열에 인덱스 생성
- 카디널리티(고유 값의 수)가 높은 열이 인덱스에 적합
- 복합 인덱스에서 열 순서는 쿼리 패턴에 맞게 설정
- 인덱스가 많으면 INSERT/UPDATE 성능이 저하됨

쿼리 최적화 기법:
- EXPLAIN 명령어로 실행 계획 분석
- 불필요한 SELECT * 대신 필요한 열만 조회
- 적절한 JOIN 유형 선택
- 서브쿼리 대신 JOIN 활용 검토
- 페이지네이션에서 OFFSET 대신 커서 기반 방식 고려

## 데이터 모델링

효과적인 데이터 모델링은 시스템의 성능과 유지보수성에 큰 영향을 미칩니다.

모델링 단계:
- 개념적 모델링: 비즈니스 요구사항을 엔티티와 관계로 표현 (ER 다이어그램)
- 논리적 모델링: 개념적 모델을 특정 DBMS에 독립적인 스키마로 변환
- 물리적 모델링: 실제 DBMS에 맞게 테이블, 인덱스, 파티션 등을 설계

관계 유형:
- 1:1 (일대일): 사용자와 프로필
- 1:N (일대다): 부서와 직원
- M:N (다대다): 학생과 수업 (중간 테이블 필요)
