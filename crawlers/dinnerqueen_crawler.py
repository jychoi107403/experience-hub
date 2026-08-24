# ==============================================================================
# 파일명: crawlers/dinnerqueen_crawler.py
# 설명: 국내 대표 맛집/숙박/뷰티 체험단 '디너의여왕(DinnerQueen)' 캠페인 크롤러
# ==============================================================================

import re
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class DinnerQueenCrawler(BaseCrawler):
    """
    디너의여왕 (https://dinnerqueen.net/taste) 실시간 캠페인 목록 수집기
    """

    def __init__(self, delay_seconds: float = 1.5):
        super().__init__(platform_name="디너의여왕", delay_seconds=delay_seconds)
        self.base_url = "https://dinnerqueen.net"

    def run(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.platform_name}] 실시간 캠페인 데이터 수집을 시작합니다...")
        campaigns = []
        target_url = f"{self.base_url}/taste"

        try:
            response = requests.get(target_url, headers=self.headers, timeout=12)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # /taste/ 경로가 포함된 상세 링크 카드들 탐색
                card_links = soup.find_all("a", href=lambda h: h and "/taste/" in h)

                for a_tag in card_links:
                    try:
                        href = a_tag["href"]
                        # 유효한 상세 페이지 URL (예: https://dinnerqueen.net/taste/1519163)
                        original_url = href if href.startswith("http") else self.base_url + href
                        
                        # taste_id 추출
                        taste_id_match = re.search(r"/taste/(\d+)", original_url)
                        if not taste_id_match:
                            continue
                        platform_id = taste_id_match.group(1)

                        # 텍스트 추출 (제목, 지역, 리워드 등)
                        card_text = a_tag.get_text(separator=" ", strip=True)
                        if not card_text or len(card_text) < 2:
                            continue

                        # 썸네일 이미지 추출
                        img_tag = a_tag.find("img")
                        image_url = ""
                        if img_tag:
                            image_url = img_tag.get("src") or img_tag.get("data-src") or ""

                        # 기본 카테고리 및 정보 추론
                        category = "맛집"
                        if any(kw in card_text for kw in ["숙박", "펜션", "호텔", "리조트"]):
                            category = "숙박/여행"
                        elif any(kw in card_text for kw in ["헤어", "미용", "피부", "뷰티", "화장품", "네일"]):
                            category = "뷰티/미용"
                        elif any(kw in card_text for kw in ["배송", "식품", "원두", "간식", "밀키트"]):
                            category = "생활/식품"

                        # 매체 형태
                        media_type = "인스타그램" if "인스타" in card_text else "블로그"

                        # 제목 정제
                        title = card_text
                        if len(title) > 60:
                            title = title[:60] + "..."

                        # 기본 마감일 (수집일로부터 5일 후로 설정)
                        end_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

                        campaign_item = {
                            "platform": self.platform_name,
                            "platform_id": platform_id,
                            "title": title,
                            "original_url": original_url,
                            "image_url": image_url,
                            "category": category,
                            "media_type": media_type,
                            "location": "서울/전국",
                            "reward": "체험 혜택 제공",
                            "capacity": 5,
                            "applied_count": 0,
                            "end_date": end_date,
                            "is_closed": False
                        }

                        # 중복 URL 체크 후 추가
                        if not any(c["original_url"] == original_url for c in campaigns):
                            campaigns.append(campaign_item)

                    except Exception as parse_err:
                        logger.debug(f"[디너의여왕] 카드 파싱 중 에러: {parse_err}")

            self.sleep()

        except Exception as e:
            logger.error(f"[{self.platform_name}] 크롤링 요청 중 오류: {e}")

        # Supabase DB 저장
        if campaigns:
            self.save_campaigns(campaigns)

        logger.info(f"[{self.platform_name}] 수집 완료! (총 {len(campaigns)}건)")
        return campaigns
