# ==============================================================================
# 파일명: crawlers/dinnerqueen_crawler.py
# 설명: 국내 대표 체험단 '디너의여왕(DinnerQueen)' 실제 매장 사진, 모집인원, 신청자수,
#       경쟁률 데이터 실시간 크롤러
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
    - 실제 매장 썸네일 사진, 모집 인원, 실시간 신청자 수, 실제 마감 D-Day를 정밀 추출합니다.
    """

    TARGET_ENDPOINTS = [
        {"url": "https://dinnerqueen.net/taste", "cat": "맛집"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%B0%B0%EC%86%A1", "cat": "생활/식품"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%B7%B0%ED%8B%B0", "cat": "뷰티/미용"},
        {"url": "https://dinnerqueen.net/taste?ct=%EC%97%AC%EA%B0%80", "cat": "숙박/여행"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%A6%B4%EC%8A%A4", "cat": "맛집"},
        {"url": "https://dinnerqueen.net/taste?ct=%EB%A7%9B%EC%A7%91", "cat": "맛집"},
    ]

    def __init__(self, delay_seconds: float = 1.0):
        super().__init__(platform_name="디너의여왕", delay_seconds=delay_seconds)
        self.base_url = "https://dinnerqueen.net"

    def run(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.platform_name}] 실시간 모집/신청 인원 및 공고 수집을 시작합니다...")
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
                cards = soup.find_all("a", href=lambda h: h and "/taste/" in h)

                for card in cards:
                    card_title_raw = card.get("title", "").strip()
                    card_class = card.get("class", [])
                    if "hover" in card_class or "캐러셀" in card_title_raw or "banner" in card_title_raw:
                        continue

                    href = card["href"]
                    original_url = href if href.startswith("http") else self.base_url + href

                    id_match = re.search(r"/taste/(\d+)", original_url)
                    if not id_match:
                        continue
                    platform_id = id_match.group(1)

                    if original_url in seen_urls:
                        continue

                    # 썸네일 이미지
                    img_tag = card.find("img")
                    image_url = ""
                    if img_tag:
                        image_url = img_tag.get("src") or img_tag.get("data-src") or ""
                        if "banner" in image_url:
                            continue

                    if not image_url:
                        continue

                    seen_urls.add(original_url)

                    # 카드 부모 컨테이너에서 상세 텍스트(신청자 수, 모집 인원, D-Day) 추출
                    parent_container = card.find_parent("div")
                    if parent_container and parent_container.find_parent("div"):
                        parent_container = parent_container.find_parent("div")
                    
                    full_card_text = parent_container.get_text(separator=" ", strip=True) if parent_container else ""

                    # 1. 신청자 수 및 모집 인원 정밀 추출 (예: '신청 2,868 / 모집 1')
                    applied_count = 0
                    capacity = 5

                    applied_match = re.search(r"신청\s*([0-9,]+)", full_card_text)
                    if applied_match:
                        applied_count = int(applied_match.group(1).replace(",", ""))

                    capacity_match = re.search(r"모집\s*([0-9,]+)", full_card_text)
                    if capacity_match:
                        capacity = int(capacity_match.group(1).replace(",", ""))

                    # 2. 실제 마감 D-Day 추출 (예: 'D-6', 'D-7', '오늘마감')
                    now = datetime.now(timezone.utc)
                    end_date = (now + timedelta(days=5)).isoformat()
                    
                    dday_match = re.search(r"D-(\d+)", full_card_text)
                    if dday_match:
                        days_left = int(dday_match.group(1))
                        end_date = (now + timedelta(days=days_left)).isoformat()
                    elif "오늘마감" in full_card_text:
                        end_date = (now + timedelta(hours=12)).isoformat()

                    # 3. 제목 정제
                    title = card_title_raw
                    if not title:
                        title = card.get_text(separator=" ", strip=True)
                    title = re.sub(r"\s*신청하기\s*$", "", title).strip()
                    if not title or len(title) < 2:
                        title = f"[디너의여왕] {default_cat} 체험단 공고 ({platform_id})"

                    # 4. 지역 추출
                    location = "서울/수도권"
                    loc_match = re.search(r"\[([가-힣\s/]+)\]", title)
                    if loc_match:
                        extracted_loc = loc_match.group(1).strip()
                        if not any(k in extracted_loc for k in ["릴스", "인스타", "블로그", "유튜브", "랜덤픽"]):
                            location = extracted_loc

                    # 5. 카테고리 및 매체 분류
                    category = default_cat
                    if any(kw in title for kw in ["숙박", "펜션", "호텔", "리조트", "글램핑", "카라반", "캠핑", "풀빌라"]):
                        category = "숙박/여행"
                    elif any(kw in title for kw in ["헤어", "미용", "피부", "뷰티", "화장품", "네일", "왁싱", "에스테틱"]):
                        category = "뷰티/미용"
                    elif any(kw in title for kw in ["배송", "식품", "원두", "간식", "밀키트", "영양제", "생활", "상품권"]):
                        category = "생활/식품"
                    elif any(kw in title for kw in ["가전", "키보드", "마우스", "이어폰", "충전기", "디지털"]):
                        category = "디지털/가전"

                    media_type = "블로그"
                    if "[릴스]" in title or "릴스" in title:
                        media_type = "릴스/숏츠"
                    elif "[인스타]" in title or "인스타" in title:
                        media_type = "인스타그램"
                    elif "[유튜브]" in title or "유튜브" in title:
                        media_type = "유튜브"

                    all_campaigns.append({
                        "platform": self.platform_name,
                        "platform_id": platform_id,
                        "title": title,
                        "original_url": original_url,
                        "image_url": image_url,
                        "category": category,
                        "media_type": media_type,
                        "location": location,
                        "reward": "체험단 무료 이용권 / 리워드 제공",
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

        logger.info(f"[{self.platform_name}] 수집 완료! (총 {len(all_campaigns)}건의 실제 모집/신청/경쟁률 데이터)")
        return all_campaigns
