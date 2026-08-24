# ==============================================================================
# 파일명: crawlers/dinnerqueen_crawler.py
# 설명: 국내 대표 체험단 '디너의여왕(DinnerQueen)' 대량 실시간 크롤러
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
    디너의여왕 (https://dinnerqueen.net) 실시간 대량 수집기
    """

    # 수집 대상 URL 목록 (메인, 맛집, 배송, 뷰티 등)
    TARGET_ENDPOINTS = [
        {"url": "https://dinnerqueen.net/taste", "cat": "맛집"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%B0%B0%EC%86%A1", "cat": "생활/식품"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%B7%B0%ED%8B%B0", "cat": "뷰티/미용"},
        {"url": "https://dinnerqueen.net/taste?ct=%EC%97%AC%EA%B0%80", "cat": "숙박/여행"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%A6%B4%EC%8A%A4", "cat": "맛집"},
    ]

    def __init__(self, delay_seconds: float = 1.0):
        super().__init__(platform_name="디너의여왕", delay_seconds=delay_seconds)
        self.base_url = "https://dinnerqueen.net"

    def run(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.platform_name}] 실시간 대량 수집을 시작합니다...")
        all_campaigns = []
        seen_urls = set()

        for ep in self.TARGET_ENDPOINTS:
            target_url = ep["url"]
            default_cat = ep["cat"]

            try:
                response = requests.get(target_url, headers=self.headers, timeout=12)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                card_links = soup.find_all("a", href=lambda h: h and "/taste/" in h)

                for a_tag in card_links:
                    href = a_tag["href"]
                    original_url = href if href.startswith("http") else self.base_url + href

                    # 고유 식별자 추출 (예: /taste/1519163)
                    taste_id_match = re.search(r"/taste/(\d+)", original_url)
                    if not taste_id_match:
                        continue
                    platform_id = taste_id_match.group(1)

                    # 중복 URL 건너뛰기
                    if original_url in seen_urls:
                        continue
                    seen_urls.add(original_url)

                    # 텍스트 정보 탐색 (a 태그 및 부모 태그 텍스트)
                    parent_box = a_tag.find_parent("div")
                    text_content = (parent_box.get_text(separator=" ", strip=True) if parent_box else "") or a_tag.get_text(separator=" ", strip=True)

                    # 썸네일 이미지 탐색
                    img_tag = a_tag.find("img") or (parent_box.find("img") if parent_box else None)
                    image_url = ""
                    if img_tag:
                        image_url = img_tag.get("src") or img_tag.get("data-src") or ""

                    # 카테고리 및 매체 분류
                    category = default_cat
                    if any(kw in text_content for kw in ["숙박", "펜션", "호텔", "리조트", "글램핑", "카라반", "캠핑"]):
                        category = "숙박/여행"
                    elif any(kw in text_content for kw in ["헤어", "미용", "피부", "뷰티", "화장품", "네일", "에스테틱"]):
                        category = "뷰티/미용"
                    elif any(kw in text_content for kw in ["배송", "식품", "원두", "간식", "밀키트", "영양제"]):
                        category = "생활/식품"

                    media_type = "인스타그램" if ("인스타" in text_content or "릴스" in text_content or "ct=릴스" in target_url) else "블로그"

                    # 지역 정보
                    location = "서울/전국"
                    loc_match = re.search(r"(서울|경기|인천|부산|대구|광주|대전|울산|세종|강원|충북|충남|전북|전남|경북|경남|제주)\s?([가-힣]+구|[가-힣]+시|[가-힣]+군)?", text_content)
                    if loc_match:
                        location = f"{loc_match.group(1)} {loc_match.group(2) or ''}".strip()
                    elif category == "생활/식품" or "배송" in text_content:
                        location = "전국(배송형)"

                    # 제목 정제
                    title = text_content if (text_content and len(text_content) > 3) else f"[디너의여왕] {category} 체험단 모집 공고 ({platform_id})"
                    if len(title) > 60:
                        title = title[:60] + "..."

                    # 마감일 (수집일 기준 5일 뒤)
                    end_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

                    all_campaigns.append({
                        "platform": self.platform_name,
                        "platform_id": platform_id,
                        "title": title,
                        "original_url": original_url,
                        "image_url": image_url,
                        "category": category,
                        "media_type": media_type,
                        "location": location,
                        "reward": "체험단 혜택 제공",
                        "capacity": 5,
                        "applied_count": 0,
                        "end_date": end_date,
                        "is_closed": False
                    })

                self.sleep()

            except Exception as e:
                logger.error(f"[{self.platform_name}] {target_url} 수집 중 오류: {e}")

        # Supabase DB에 배치 저장
        if all_campaigns:
            self.save_campaigns(all_campaigns)

        logger.info(f"[{self.platform_name}] 전체 수집 완료! (총 {len(all_campaigns)}건)")
        return all_campaigns
