# ==============================================================================
# 파일명: main.py
# 설명: 모든 체험단 플랫폼 크롤러를 일괄 실행하거나 선택 실행하는 메인 프로그램
# 실행 방법: python main.py
# ==============================================================================

import sys
import logging

# Windows 콘솔에서 한글 및 이모지 출력 시 인코딩 오류(cp949) 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from crawlers import RevuCrawler, GangnamCrawler, DinnerQueenCrawler

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 65)
    print(" [Experience Hub Crawler] 국내 체험단 데이터 수집기 가동 ")
    print("=" * 65)

    # 실행할 크롤러 인스턴스 목록 등록
    active_crawlers = [
        DinnerQueenCrawler(delay_seconds=1.0),  # 디너의여왕 크롤러 (실시간 파싱 지원)
        RevuCrawler(delay_seconds=1.5),         # 레뷰 크롤러
        GangnamCrawler(delay_seconds=1.5),      # 강남맛집 크롤러
    ]

    total_collected = 0

    # 각 크롤러 순차 실행
    for crawler in active_crawlers:
        print(f"\n▶ [{crawler.platform_name}] 데이터 수집 시작...")
        try:
            results = crawler.run()
            total_collected += len(results)
        except Exception as e:
            logger.error(f"[{crawler.platform_name}] 크롤러 실행 중 예외 발생: {e}")

    print("\n" + "=" * 65)
    print(f" [완료] 모든 크롤링 작업이 끝났습니다! (총 수집 건수: {total_collected}건)")
    print("=" * 65)


if __name__ == "__main__":
    main()
