"""
Base Parser

로그 파서의 기본 인터페이스 정의
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from common.models import ApiCall, LogEntry


class ParserError(Exception):
    """파서 에러"""

    pass


class BaseLogParser(ABC):
    """로그 파서 기본 클래스"""

    @abstractmethod
    def can_parse(self, log_text: str) -> bool:
        """
        이 파서로 파싱 가능한지 확인

        Args:
            log_text: 로그 텍스트

        Returns:
            파싱 가능 여부
        """
        pass

    @abstractmethod
    def parse(self, log_text: str, source_file: Optional[str] = None) -> List[ApiCall]:
        """
        로그 텍스트를 파싱하여 API 호출 목록 추출

        Args:
            log_text: 로그 텍스트
            source_file: 로그 소스 파일명

        Returns:
            추출된 API 호출 목록

        Raises:
            ParserError: 파싱 실패 시
        """
        pass

    def parse_file(self, file_path: str) -> List[ApiCall]:
        """
        로그 파일을 읽어서 파싱

        Args:
            file_path: 로그 파일 경로

        Returns:
            추출된 API 호출 목록

        Raises:
            ParserError: 파일 읽기 또는 파싱 실패 시
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                log_text = f.read()
            return self.parse(log_text, source_file=file_path)
        except FileNotFoundError:
            raise ParserError(f"파일을 찾을 수 없습니다: {file_path}")
        except Exception as e:
            raise ParserError(f"파일 읽기 실패: {e}")

    def _create_log_entries(
        self, log_text: str, source_file: Optional[str] = None
    ) -> List[LogEntry]:
        """
        로그 텍스트를 LogEntry 목록으로 변환

        Args:
            log_text: 로그 텍스트
            source_file: 소스 파일명

        Returns:
            LogEntry 목록
        """
        entries = []
        for line_number, line in enumerate(log_text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue

            entry = LogEntry(
                raw_text=line,
                line_number=line_number,
                source_file=source_file,
            )
            entries.append(entry)

        return entries
