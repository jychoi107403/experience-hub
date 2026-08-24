# ==============================================================================
# 파일명: crawlers/reviewnote_crawler.py
# 설명: 국내 대표 체험단 플랫폼 '리뷰노트(ReviewNote)' 실시간 캠페인 크롤러
# ==============================================================================

import re
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class ReviewNoteCrawler(BaseCrawler):
    """
    리뷰노트 (https://www.reviewnote.co.kr) 실시간 캠페인 수집기
    """

    def __init__(self, delay_seconds: float = 1.2, max_pages: int = 3):
        super().__init__(platform_name="리뷰노트", delay_seconds=delay_seconds)
        self.base_url = "https://www.reviewnote.co.kr"
        self.max_pages = max_pages

    def parse_page(self, html_text: str) -> List[Dict[str, Any]]:
        page_campaigns = []
        soup = BeautifulSoup(html_text, "html.parser")

        # 캠페인 카드 요소 검색 (a 태그 중 campaign 상세 링크를 가진 것들)
        cards = soup.find_all("a", href=lambda h: h and ("/campaign/" in h or "/detail/" in h or "/item/" in h))

        for card in cards:
            try:
                href = card["href"]
                original_url = href if href.startswith("http") else self.base_url + href

                # 고유 식별자 추출
                id_match = re.search(r"/(?:campaign|detail|item)/([a-zA-Z0-9_\-]+)", original_url)
                platform_id = id_match.group(1) if id_match else None

                card_text = card.get_text(separator=" ", strip=True)
                if not card_text or len(card_text) < 3:
                    continue

                # 썸네일 이미지 추출
                img_tag = card.find("img")
                image_url = ""
                if img_tag:
                    image_url = img_tag.get("src") or img_tag.get("data-src") or ""
                    if image_url and not image_url.startswith("http"):
                        image_url = self.base_url + image_url

                # 카테고리 추출
                category = "맛집"
                if any(kw in card_text for kw in ["숙박", "펜션", "호텔", "리조트", "여행", "캠핑"]):
                    category = "숙박/여행"
                elif any(kw in card_text for kw in ["뷰티", "헤어", "미용", "피부", "화장품", "네일", "에스테틱"]):
                    category = "뷰티/미용"
                elif any(kw in card_text for kw in ["배송", "식품", "원두", "간식", "밀키트", "생활", "리빙"]):
                    category = "생활/식품"
                elif any(kw in card_text for kw in ["디지털", "가전", "IT", "전자기기"]):
                    category = "디지털/가전"

                # 리뷰 매체
                media_type = "블로그"
                if "인스타" in card_text:
                    media_type = "인스타그램"
                elif "릴스" in card_text or "숏츠" in card_text:
                    media_type = "릴스/숏츠"
                elif "유튜브" in card_text:
                    media_type = "유튜브"

                # 지역 정보
                location = "서울/전국"
                loc_match = re.search(r"(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주)\s?([가-힣]+구|[가-힣]+시)?", card_text)
                if loc_match:
                    location = f"{loc_match.group(1)} {loc_match.group(2) or ''}".strip()
                elif category == "생활/식품" or "배송" in card_text:
                    location = "전국(배송형)"

                # 제목
                title = card_text
                if len(title) > 65:
                    title = title[:65] + "..."

                end_date = (datetime.now(timezone.utc) + timedelta(days=6)).isoformat()

                page_campaigns.append({
                    "platform": self.platform_name,
                    "platform_id": platform_id,
                    "title": title,
                    "original_url": original_url,
                    "image_url": image_url,
                    "category": category,
                    "media_type": media_type,
                    "location": location,
                    "reward": "체험단 혜택 제공",
                    "capacity": 10,
                    "applied_count": 0,
                    "end_date": end_date,
                    "is_closed": False
                })
            except Exception as e:
                logger.debug(f"[리뷰노트] 파싱 중 에러: {e}")

        return page_campaigns

    def run(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.platform_name}] 실시간 캠페인 수집을 시작합니다... (최대 {self.max_pages}페이지)")
        all_campaigns = []
        seen_urls = set()

        for page in range(1, self.max_pages + 1):
            target_url = f"{self.base_url}?page={page}"
            try:
                response = requests.get(target_url, headers=self.headers, timeout=12)
                if response.status_code == 200:
                    items = self.parse_page(response.text)
                    new_count = 0
                    for item in items:
                        if item["original_url"] not in seen_urls:
                            seen_urls.add(item["original_url"])
                            all_campaigns.append(item)
                            new_count += 1
                    logger.info(f"[{self.platform_name}] {page}페이지 수집: 신규 {new_count}건")
                self.sleep()
            except Exception as e:
                logger.error(f"[{self.platform_name}] {page}페이지 수집 실패: {e}")

        # Supabase DB 저장
        if all_campaigns:
            self.save_campaigns(all_campaigns)

        logger.info(f"[{self.platform_name}] 전체 수집 완료! (총 {len(all_campaigns)}건)")
        return all_campaigns
