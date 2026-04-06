"""
docs/ 디렉토리의 문서들이 올바르게 구성되어 있는지 검증하는 테스트.

RAGAS testset generation에 사용되는 샘플 문서들의 구조와 내용을 확인합니다.
"""

import os
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).parent.parent / "docs"

# 기대하는 문서 파일 목록
EXPECTED_DOCS = [
    "python_basics.md",
    "machine_learning_basics.md",
    "web_api_design.md",
    "database_fundamentals.md",
    "docker_containers.md",
    "git_version_control.md",
]

MIN_DOC_LENGTH = 500  # 최소 문자 수 (testset generation에 충분한 내용)
MIN_SECTION_COUNT = 3  # 최소 섹션(## 헤더) 수


def get_markdown_files():
    """docs/ 디렉토리의 모든 마크다운 파일을 반환합니다."""
    return sorted(DOCS_DIR.glob("**/*.md"))


class TestDocsDirectory:
    """docs/ 디렉토리 구조 검증"""

    def test_docs_directory_exists(self):
        assert DOCS_DIR.is_dir(), "docs/ 디렉토리가 존재해야 합니다"

    def test_expected_documents_exist(self):
        existing = {f.name for f in get_markdown_files()}
        for doc in EXPECTED_DOCS:
            assert doc in existing, f"docs/{doc} 파일이 존재해야 합니다"

    def test_minimum_document_count(self):
        files = get_markdown_files()
        assert len(files) >= 6, (
            f"docs/ 디렉토리에 최소 6개의 문서가 있어야 합니다 (현재: {len(files)}개)"
        )


class TestDocumentContent:
    """각 문서의 내용 검증"""

    @pytest.fixture(params=EXPECTED_DOCS)
    def doc_path(self, request):
        return DOCS_DIR / request.param

    def test_document_is_readable_utf8(self, doc_path):
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) > 0, f"{doc_path.name}이 비어 있으면 안 됩니다"

    def test_document_has_title(self, doc_path):
        content = doc_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert lines[0].startswith("# "), (
            f"{doc_path.name}은 '# 제목'으로 시작해야 합니다"
        )

    def test_document_has_sufficient_content(self, doc_path):
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) >= MIN_DOC_LENGTH, (
            f"{doc_path.name}은 최소 {MIN_DOC_LENGTH}자 이상이어야 합니다 "
            f"(현재: {len(content)}자)"
        )

    def test_document_has_sections(self, doc_path):
        content = doc_path.read_text(encoding="utf-8")
        sections = [line for line in content.split("\n") if line.startswith("## ")]
        assert len(sections) >= MIN_SECTION_COUNT, (
            f"{doc_path.name}에 최소 {MIN_SECTION_COUNT}개의 섹션(##)이 있어야 합니다 "
            f"(현재: {len(sections)}개)"
        )

    def test_document_has_no_empty_sections(self, doc_path):
        content = doc_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("## "):
                # 섹션 헤더 다음에 빈 줄 이후 내용이 있어야 함
                remaining = "\n".join(lines[i + 1 :]).strip()
                # 다음 섹션까지의 내용을 확인
                section_content = []
                for next_line in lines[i + 1 :]:
                    if next_line.startswith("## ") or next_line.startswith("# "):
                        break
                    section_content.append(next_line)
                section_text = "\n".join(section_content).strip()
                assert len(section_text) > 0, (
                    f"{doc_path.name}의 '{line.strip()}' 섹션이 비어 있습니다"
                )


class TestDocumentDiversity:
    """문서들의 다양성 검증"""

    def test_documents_cover_different_topics(self):
        """각 문서의 제목이 서로 다른지 확인합니다."""
        titles = []
        for doc in EXPECTED_DOCS:
            content = (DOCS_DIR / doc).read_text(encoding="utf-8")
            title = content.strip().split("\n")[0]
            titles.append(title)
        assert len(set(titles)) == len(titles), "모든 문서가 고유한 제목을 가져야 합니다"

    def test_langchain_loader_compatibility(self):
        """DirectoryLoader가 문서를 로드할 수 있는 형식인지 확인합니다."""
        for md_file in get_markdown_files():
            content = md_file.read_text(encoding="utf-8")
            # TextLoader가 읽을 수 있도록 유효한 UTF-8이어야 함
            assert isinstance(content, str)
            assert len(content) > 0
            # 파일 확장자가 .md여야 함 (glob="**/*.md" 패턴과 일치)
            assert md_file.suffix == ".md"
