# ==============================================================================
# 파일명: crawlers/gangnam_crawler.py
# 설명: 국내 인기 맛집/뷰티 체험단 플랫폼 '강남맛집'의 캠페인 데이터를 수집하는 크롤러
# ==============================================================================

import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)


class GangnamCrawler(BaseCrawler):
    """
    강남맛집 체험단 사이트에서 최신 캠페인 공고를 수집하는 크롤러입니다.
    """

    def __init__(self, delay_seconds: float = 1.5):
        # 부모 클래스(BaseCrawler) 초기화
        super().__init__(platform_name="강남맛집", delay_seconds=delay_seconds)
        self.base_url = "https://xn--939au0g4vj8sq.net"  # 강남맛집.net 퓨니코드

    def run(self) -> List[Dict[str, Any]]:
        """
        강남맛집 크롤링을 실행하고 수집된 데이터를 반환 및 DB에 저장합니다.
        """
        logger.info(f"[{self.platform_name}] 캠페인 데이터 수집을 시작합니다...")
        campaigns = []

        try:
            # 메인 캠페인 목록 페이지 요청
            target_url = f"{self.base_url}/cp"
            response = requests.get(target_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # 캠페인 카드 리스트 탐색
                items = soup.select(".cp_list_item, .item, [class*='campaign']")

                for item in items:
                    try:
                        # 1. 상세 링크
                        a_tag = item.find("a", href=True)
                        if not a_tag:
                            continue
                        link = a_tag["href"]
                        if not link.startswith("http"):
                            link = self.base_url + link

                        # 2. 제목
                        title_elem = item.find(class_=lambda c: c and ("title" in c or "subject" in c))
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        if not title:
                            continue

                        # 3. 썸네일 이미지
                        img_elem = item.find("img")
                        img_url = ""
                        if img_elem:
                            img_url = img_elem.get("src") or img_elem.get("data-src") or ""
                            if img_url and not img_url.startswith("http"):
                                img_url = self.base_url + img_url

                        # 4. 지역 및 제공 내역
                        loc_elem = item.find(class_=lambda c: c and ("area" in c or "loc" in c))
                        location = loc_elem.get_text(strip=True) if loc_elem else "서울/수도권"

                        reward_elem = item.find(class_=lambda c: c and ("reward" in c or "benefit" in c))
                        reward = reward_elem.get_text(strip=True) if reward_elem else "방문 체험 제공"

                        campaigns.append({
                            "platform": self.platform_name,
                            "title": title,
                            "original_url": link,
                            "image_url": img_url,
                            "category": "맛집",
                            "media_type": "블로그",
                            "location": location,
                            "reward": reward,
                            "capacity": 5,
                            "applied_count": 0,
                            "is_closed": False
                        })
                    except Exception as parse_err:
                        logger.debug(f"[강남맛집] 카드 파싱 중 경미한 에러: {parse_err}")

            self.sleep()
        except Exception as e:
            logger.error(f"[{self.platform_name}] 수집 중 에러 발생: {e}")

        # Supabase에 데이터 저장
        if campaigns:
            self.save_campaigns(campaigns)

        logger.info(f"[{self.platform_name}] 수집 완료! (총 {len(campaigns)}건)")
        return campaigns
