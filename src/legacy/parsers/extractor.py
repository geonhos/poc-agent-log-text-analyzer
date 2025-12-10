"""
API Call Extractor

여러 파서를 통합하여 로그에서 API 호출 정보 자동 추출
"""

from typing import List, Optional

from common.models import ApiCall

from .base import BaseLogParser, ParserError
from .http_parser import HttpRequestParser
from .json_parser import JsonLogParser
from .text_parser import TextLogParser


class ApiCallExtractor:
    """
    API 호출 정보 자동 추출기

    여러 파서를 시도하여 로그 형식을 자동 감지하고 파싱
    """

    def __init__(self, parsers: Optional[List[BaseLogParser]] = None):
        """
        Args:
            parsers: 사용할 파서 목록 (기본값: 모든 내장 파서)
        """
        if parsers is None:
            # 기본 파서들 (우선순위 순)
            self.parsers = [
                JsonLogParser(),  # JSON이 가장 명확하므로 먼저
                HttpRequestParser(),  # HTTP request dump
                TextLogParser(),  # 일반 텍스트 (가장 유연함)
            ]
        else:
            self.parsers = parsers

    def extract(self, log_text: str, source_file: Optional[str] = None) -> List[ApiCall]:
        """
        로그에서 API 호출 정보 추출

        자동으로 적절한 파서를 선택하여 파싱합니다.

        Args:
            log_text: 로그 텍스트
            source_file: 로그 소스 파일명

        Returns:
            추출된 API 호출 목록

        Raises:
            ParserError: 모든 파서가 실패한 경우
        """
        if not log_text or not log_text.strip():
            return []

        # 각 파서를 순서대로 시도
        for parser in self.parsers:
            if parser.can_parse(log_text):
                try:
                    api_calls = parser.parse(log_text, source_file)
                    if api_calls:
                        return api_calls
                except ParserError:
                    # 이 파서는 실패, 다음 파서 시도
                    continue

        # 모든 파서가 실패하거나 아무것도 추출하지 못함
        raise ParserError("로그에서 API 호출 정보를 추출할 수 없습니다")

    def extract_from_file(self, file_path: str) -> List[ApiCall]:
        """
        로그 파일에서 API 호출 정보 추출

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
            return self.extract(log_text, source_file=file_path)
        except FileNotFoundError:
            raise ParserError(f"파일을 찾을 수 없습니다: {file_path}")
        except Exception as e:
            raise ParserError(f"파일 읽기 실패: {e}")

    def detect_format(self, log_text: str) -> Optional[str]:
        """
        로그 형식 감지

        Args:
            log_text: 로그 텍스트

        Returns:
            감지된 형식 이름 또는 None
        """
        for parser in self.parsers:
            if parser.can_parse(log_text):
                return parser.__class__.__name__

        return None
