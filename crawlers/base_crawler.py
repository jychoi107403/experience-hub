# ==============================================================================
# 파일명: crawlers/base_crawler.py
# 설명: 모든 체험단 사이트 크롤러가 공통으로 상속받아 사용하는 베이스(기반) 클래스
# 주요 기능: Supabase DB 연결, 데이터 Upsert(중복 시 업데이트/신규 시 삽입), 요청 딜레이
# ==============================================================================

import os
import time
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# 로깅 기본 설정 (콘솔에 진행 상황을 보기 쉽게 출력)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class BaseCrawler:
    """
    모든 개별 사이트 크롤러의 부모 클래스입니다.
    데이터베이스 통신 및 공통 유틸리티 기능을 제공합니다.
    """

    def __init__(self, platform_name: str, delay_seconds: float = 1.0):
        """
        초기화 메서드
        :param platform_name: 체험단 플랫폼 이름 (예: '레뷰', '강남맛집')
        :param delay_seconds: 서버 부하 방지를 위한 각 요청 간 대기 시간 (초 단위)
        """
        self.platform_name = platform_name
        self.delay_seconds = delay_seconds

        # .env 파일에서 환경변수 로드
        load_dotenv()

        # Supabase 접속 정보 확인
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        self.supabase: Optional[Client] = None
        self._init_supabase_client()

        # 웹 요청 시 봇 차단을 방지하기 위한 기본 브라우저 User-Agent 헤더
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _init_supabase_client(self):
        """
        Supabase 데이터베이스 클라이언트를 안전하게 초기화합니다.
        """
        if not self.supabase_url or not self.supabase_key:
            logger.warning(
                f"[{self.platform_name}] SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다. "
                f"DB 저장이 비활성화되며 로컬 콘솔 출력 모드로 동작합니다."
            )
            return

        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info(f"[{self.platform_name}] Supabase 클라이언트 연결 성공!")
        except Exception as e:
            logger.error(f"[{self.platform_name}] Supabase 클라이언트 초기화 실패: {e}")
            self.supabase = None

    def sleep(self):
        """
        상대 사이트 서버에 부하를 주지 않도록 매너 있게 잠시 대기합니다.
        """
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)

    def save_campaigns(self, campaigns: List[Dict[str, Any]]) -> int:
        """
        수집된 캠페인 데이터 목록을 Supabase DB의 campaigns 테이블에 저장합니다.
        중복된 original_url이 있으면 최신 데이터로 업데이트(Upsert)합니다.

        :param campaigns: 캠페인 딕셔너리 리스트
        :return: 성공적으로 저장/갱신된 건수
        """
        if not campaigns:
            logger.info(f"[{self.platform_name}] 저장할 캠페인 데이터가 없습니다.")
            return 0

        # DB가 연결되지 않은 경우 콘솔에만 출력
        if not self.supabase:
            logger.info(f"[{self.platform_name}] [로컬 모드] {len(campaigns)}건의 데이터를 수집했습니다:")
            for idx, c in enumerate(campaigns[:3], 1):
                logger.info(f"  {idx}. [{c.get('category')}] {c.get('title')} ({c.get('location')}) - {c.get('original_url')}")
            if len(campaigns) > 3:
                logger.info(f"  ... 외 {len(campaigns) - 3}건 생략")
            return len(campaigns)

        saved_count = 0
        try:
            # Supabase의 upsert 기능 사용: original_url이 같은 데이터가 있으면 갱신, 없으면 삽입
            response = self.supabase.table("campaigns").upsert(
                campaigns,
                on_conflict="original_url"
            ).execute()

            if response.data:
                saved_count = len(response.data)
                logger.info(f"[{self.platform_name}] 성공적으로 {saved_count}건의 캠페인을 DB에 저장/갱신했습니다.")
            else:
                logger.info(f"[{self.platform_name}] DB 작업 완료 (응답 데이터 없음)")

        except Exception as e:
            logger.error(f"[{self.platform_name}] Supabase DB 저장 중 오류 발생: {e}")

        return saved_count

    def run(self) -> List[Dict[str, Any]]:
        """
        자식 클래스에서 반드시 구현해야 하는 크롤링 실행 메서드입니다.
        """
        raise NotImplementedError("각 크롤러 클래스에서 run() 메서드를 직접 구현해야 합니다.")
