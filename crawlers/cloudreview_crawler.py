# ==============================================================================
# 파일명: crawlers/cloudreview_crawler.py
# 설명: 국내 대표 메이저 체험단 '클라우드리뷰(CloudReview)' 실시간 캠페인 크롤러
# ==============================================================================

import re
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class CloudReviewCrawler(BaseCrawler):
    """
    클라우드리뷰 (https://cloudreview.co.kr) 실시간 대량 수집기
    - 실제 매장/제품 썸네일(data-original), 제목, 제공혜택, 모집인원, 신청인원, D-Day를 정밀 추출합니다.
    """

    TARGET_ENDPOINTS = [
        {"url": "https://cloudreview.co.kr", "media": "블로그", "default_cat": "맛집"},
        {"url": "https://cloudreview.co.kr/campaign/blog", "media": "블로그", "default_cat": "맛집"},
        {"url": "https://cloudreview.co.kr/campaign/instagram", "media": "인스타그램", "default_cat": "뷰티/미용"},
        {"url": "https://cloudreview.co.kr/campaign/short", "media": "릴스/숏츠", "default_cat": "맛집"},
        {"url": "https://cloudreview.co.kr/campaign/buy", "media": "블로그", "default_cat": "생활/식품"},
    ]

    def __init__(self, delay_seconds: float = 1.0):
        super().__init__(platform_name="클라우드리뷰", delay_seconds=delay_seconds)
        self.base_url = "https://cloudreview.co.kr"

    def run(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.platform_name}] 실시간 대량 수집을 시작합니다...")
        all_campaigns = []
        seen_urls = set()

        for ep in self.TARGET_ENDPOINTS:
            target_url = ep["url"]
            media_type = ep["media"]
            default_cat = ep["default_cat"]

            try:
                response = requests.get(target_url, headers=self.headers, timeout=12)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("a", href=lambda h: h and "/campaign/detail/" in h)

                for card in cards:
                    href = card["href"]
                    original_url = href if href.startswith("http") else self.base_url + href

                    id_match = re.search(r"/campaign/detail/(\d+)", original_url)
                    if not id_match:
                        continue
                    platform_id = id_match.group(1)

                    if original_url in seen_urls:
                        continue

                    # 카드 컨테이너 탐색 (부모의 부모 컨테이너)
                    card_box = card.find_parent("div")
                    if card_box and card_box.find_parent("div"):
                        card_box = card_box.find_parent("div")

                    if not card_box:
                        continue

                    # 1. 썸네일 이미지 추출 (data-original 또는 src)
                    img_tag = card_box.find("img")
                    image_url = ""
                    if img_tag:
                        image_url = img_tag.get("data-original") or img_tag.get("src") or img_tag.get("data-src") or ""
                        if image_url and not image_url.startswith("http"):
                            image_url = self.base_url + image_url

                    if not image_url or "icon" in image_url or "banner" in image_url:
                        continue

                    seen_urls.add(original_url)

                    # 2. 텍스트 정보 파싱
                    box_text = card_box.get_text(separator=" | ", strip=True)
                    text_parts = [p.strip() for p in box_text.split("|") if p.strip()]

                    # 제목 및 혜택 추출
                    title = ""
                    reward = ""
                    if len(text_parts) >= 2:
                        title = text_parts[0]
                        reward = text_parts[1]
                    elif len(text_parts) == 1:
                        title = text_parts[0]

                    if not title or len(title) < 2:
                        title = card.get_text(strip=True) or f"[클라우드리뷰] {default_cat} 체험단 공고 ({platform_id})"

                    # 3. 모집 인원 및 신청 인원 정밀 추출 (예: '7인 모집', '779인 참여')
                    capacity = 5
                    applied_count = 0

                    cap_match = re.search(r"(\d+)\s*인\s*모집|모집\s*(\d+)", box_text)
                    if cap_match:
                        capacity = int(cap_match.group(1) or cap_match.group(2))

                    app_match = re.search(r"(\d+)\s*인\s*참여|신청\s*(\d+)", box_text)
                    if app_match:
                        applied_count = int(app_match.group(1) or app_match.group(2))

                    # 4. 마감 D-Day 추출 (예: '2일남음', 'D-3', '오늘마감')
                    now = datetime.now(timezone.utc)
                    end_date = (now + timedelta(days=5)).isoformat()

                    day_match = re.search(r"(\d+)\s*일남음|D-(\d+)", box_text)
                    if day_match:
                        days = int(day_match.group(1) or day_match.group(2))
                        end_date = (now + timedelta(days=days)).isoformat()
                    elif "오늘마감" in box_text or "0일남음" in box_text:
                        end_date = (now + timedelta(hours=12)).isoformat()

                    # 5. 지역 및 카테고리 분류
                    location = "서울/수도권"
                    if "배송" in box_text or "#배송형" in box_text:
                        location = "전국(배송형)"
                    else:
                        loc_match = re.search(r"\[([가-힣\s/]+)\]", title)
                        if loc_match:
                            location = loc_match.group(1).strip()

                    category = default_cat
                    if any(kw in (title + reward + box_text) for kw in ["숙박", "펜션", "호텔", "리조트", "글램핑", "카라반", "캠핑"]):
                        category = "숙박/여행"
                    elif any(kw in (title + reward + box_text) for kw in ["헤어", "미용", "피부", "뷰티", "화장품", "네일", "에스테틱", "세럼", "크림"]):
                        category = "뷰티/미용"
                    elif any(kw in (title + reward + box_text) for kw in ["배송", "식품", "원두", "간식", "밀키트", "영양제", "생활", "리빙", "수저", "세트"]):
                        category = "생활/식품"
                    elif any(kw in (title + reward + box_text) for kw in ["가전", "키보드", "마우스", "이어폰", "충전기", "디지털"]):
                        category = "디지털/가전"

                    all_campaigns.append({
                        "platform": self.platform_name,
                        "platform_id": platform_id,
                        "title": title,
                        "original_url": original_url,
                        "image_url": image_url,
                        "category": category,
                        "media_type": media_type,
                        "location": location,
                        "reward": reward or "체험단 무료 이용권 / 제품 제공",
                        "capacity": capacity,
                        "applied_count": applied_count,
                        "end_date": end_date,
                        "is_closed": False
                    })

                self.sleep()

            except Exception as e:
                logger.error(f"[{self.platform_name}] {target_url} 수집 중 오류: {e}")

        # Supabase DB에 배치 저장
        if all_campaigns:
            self.save_campaigns(all_campaigns)

        logger.info(f"[{self.platform_name}] 전체 수집 완료! (총 {len(all_campaigns)}건의 공고)")
        return all_campaigns
