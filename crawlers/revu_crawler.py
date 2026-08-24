# ==============================================================================
# 파일명: crawlers/revu_crawler.py
# 설명: 국내 1위 체험단 플랫폼 '레뷰(Revu)'의 캠페인 데이터를 수집하는 크롤러
# ==============================================================================

import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class RevuCrawler(BaseCrawler):
    """
    레뷰(Revu, https://www.revu.net) 사이트에서 공개된 최신 캠페인 공고를 수집하는 크롤러입니다.
    """

    def __init__(self, delay_seconds: float = 1.5):
        # 부모 클래스(BaseCrawler) 초기화
        super().__init__(platform_name="레뷰", delay_seconds=delay_seconds)
        self.base_url = "https://www.revu.net"

    def parse_campaign_card(self, item_soup) -> Dict[str, Any]:
        """
        HTML 카드 요소에서 개별 체험단 캠페인 정보를 추출합니다.
        """
        try:
            # 1. 상세 페이지 링크 추출
            link_tag = item_soup.find("a", href=True)
            if not link_tag:
                return {}
            original_url = link_tag["href"]
            if not original_url.startswith("http"):
                original_url = self.base_url + original_url

            # 2. 제목 추출
            title_tag = item_soup.find(class_=lambda c: c and ("title" in c.lower() or "subject" in c.lower()))
            title = title_tag.get_text(strip=True) if title_tag else "제목 정보 없음"

            # 3. 썸네일 이미지 URL 추출
            img_tag = item_soup.find("img")
            image_url = ""
            if img_tag:
                image_url = img_tag.get("src") or img_tag.get("data-src") or ""
                if image_url and not image_url.startswith("http"):
                    image_url = self.base_url + image_url

            # 4. 카테고리 및 매체 추출
            category = "기타"
            media_type = "블로그"
            badge_tag = item_soup.find(class_=lambda c: c and ("badge" in c.lower() or "cate" in c.lower() or "channel" in c.lower()))
            if badge_tag:
                badge_text = badge_tag.get_text(strip=True)
                if "인스타" in badge_text:
                    media_type = "인스타그램"
                elif "유튜브" in badge_text:
                    media_type = "유튜브"
                elif "릴스" in badge_text or "숏츠" in badge_text:
                    media_type = "릴스/숏츠"

            # 5. 제공 혜택 / 리워드 추출
            reward_tag = item_soup.find(class_=lambda c: c and ("reward" in c.lower() or "benefit" in c.lower() or "desc" in c.lower()))
            reward = reward_tag.get_text(strip=True) if reward_tag else ""

            # 6. 지역 정보 추출
            location_tag = item_soup.find(class_=lambda c: c and ("location" in c.lower() or "area" in c.lower() or "local" in c.lower()))
            location = location_tag.get_text(strip=True) if location_tag else "전국(배송/기타)"

            # 데이터 딕셔너리 조립
            campaign_data = {
                "platform": self.platform_name,
                "title": title,
                "original_url": original_url,
                "image_url": image_url,
                "category": category,
                "media_type": media_type,
                "location": location,
                "reward": reward,
                "capacity": 10,
                "applied_count": 0,
                "is_closed": False
            }

            return campaign_data

        except Exception as e:
            logger.debug(f"[레뷰] 항목 파싱 중 경미한 오류: {e}")
            return {}

    def fetch_api_campaigns(self) -> List[Dict[str, Any]]:
        """
        레뷰의 공개 모바일/웹 API 엔드포인트(JSON)가 있는 경우 고속으로 수집합니다.
        (웹페이지 HTML 변경에 영향을 덜 받아 더 안정적입니다)
        """
        campaigns = []
        api_url = "https://api.revu.net/campaign/list"  # 대표 API 구조

        try:
            params = {
                "page": 1,
                "limit": 20,
                "order": "recent"
            }
            response = requests.get(api_url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", {}).get("list", []) or data.get("items", [])
                for item in items:
                    c_id = item.get("id") or item.get("campaign_id")
                    title = item.get("title") or item.get("name")
                    if not title:
                        continue

                    detail_url = item.get("url") or f"https://www.revu.net/campaign/{c_id}"
                    img_url = item.get("banner_image") or item.get("image_url") or item.get("thumbnail")
                    category = item.get("category_name") or item.get("category") or "기타"
                    reward = item.get("benefit") or item.get("reward") or item.get("offer_description", "")
                    location = item.get("location") or item.get("area_name") or "전국(배송형)"
                    capacity = item.get("recruiting_count") or item.get("capacity") or 0
                    applied = item.get("applied_count") or 0

                    campaigns.append({
                        "platform": self.platform_name,
                        "platform_id": str(c_id) if c_id else None,
                        "title": title,
                        "original_url": detail_url,
                        "image_url": img_url,
                        "category": category,
                        "media_type": "블로그",
                        "location": location,
                        "reward": reward,
                        "capacity": int(capacity),
                        "applied_count": int(applied),
                        "is_closed": False
                    })
        except Exception as e:
            logger.debug(f"[레뷰] API 요청 시도 종료 (HTML 수집 모드로 대체): {e}")

        return campaigns

    def run(self) -> List[Dict[str, Any]]:
        """
        레뷰 크롤링을 실행하고 수집된 데이터를 반환합니다.
        """
        logger.info(f"[{self.platform_name}] 캠페인 데이터 수집을 시작합니다...")
        all_campaigns = []

        # 1. API 수집 시도
        api_results = self.fetch_api_campaigns()
        if api_results:
            all_campaigns.extend(api_results)
            logger.info(f"[{self.platform_name}] API를 통해 {len(api_results)}건을 수집했습니다.")

        # 2. HTML 메인 페이지 수집 시도 (API 데이터가 부족하거나 없을 경우)
        if len(all_campaigns) < 5:
            try:
                response = requests.get(self.base_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # 카드 형태의 공고 아이템 검색
                    card_elements = soup.select(".campaign-item, .item-card, [class*='campaign'], [class*='Card']")
                    for card in card_elements:
                        item_data = self.parse_campaign_card(card)
                        if item_data and item_data.get("original_url"):
                            all_campaigns.append(item_data)
                self.sleep()
            except Exception as e:
                logger.error(f"[{self.platform_name}] 웹페이지 수집 중 오류 발생: {e}")

        # 3. 데이터베이스(Supabase)에 일괄 저장
        if all_campaigns:
            self.save_campaigns(all_campaigns)

        logger.info(f"[{self.platform_name}] 수집 완료! (총 {len(all_campaigns)}건)")
        return all_campaigns
