# ==============================================================================
# 파일명: main.py
# 설명: 모든 체험단 플랫폼 크롤러를 일괄 실행하고, 마감 공고를 정리하며,
#       상세 수집 통계를 리포트하는 통합 프로그램
# 실행 방법: python main.py
# ==============================================================================

import sys
import time
import logging

# Windows 콘솔 인코딩 대응
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from crawlers import (
    BaseCrawler,
    DinnerQueenCrawler,
    CloudReviewCrawler,
    ReviewNoteCrawler,
    RevuCrawler,
    GangnamCrawler,
)

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    start_time = time.time()
    print("=" * 70)
    print(" [Experience Hub] 국내 체험단 대량 데이터 수집 및 동기화 가동 ")
    print("=" * 70)

    # 1. 실행할 크롤러 목록 등록
    crawlers = [
        DinnerQueenCrawler(delay_seconds=1.0),   # 디너의여왕 (120건 실제 매장 수집)
        CloudReviewCrawler(delay_seconds=1.0),   # 클라우드리뷰 (블로그/인스타/릴스 수집)
        ReviewNoteCrawler(delay_seconds=1.2),    # 리뷰노트
        RevuCrawler(delay_seconds=1.5),          # 레뷰
        GangnamCrawler(delay_seconds=1.5),       # 강남맛집
    ]

    stats = {}
    total_collected = 0

    # 2. 각 플랫폼 크롤러 순차 실행
    for crawler in crawlers:
        platform = crawler.platform_name
        print(f"\n▶ [{platform}] 데이터 수집 시작...")
        try:
            results = crawler.run()
            count = len(results)
            stats[platform] = count
            total_collected += count
        except Exception as e:
            logger.error(f"[{platform}] 크롤러 실행 중 예외 발생: {e}")
            stats[platform] = 0

    # 3. 마감 기한이 지난 공고 자동 정리(Clean-up)
    print("\n🧹 [데이터베이스] 마감 기한이 지난 공고 자동 정리 작업 진행 중...")
    cleaner = BaseCrawler(platform_name="시스템정리")
    closed_count = cleaner.cleanup_closed_campaigns()

    elapsed = round(time.time() - start_time, 2)

    # 4. 종합 결과 통계 리포트 출력
    print("\n" + "=" * 70)
    print(" 📊 [Experience Hub] 수집 및 동기화 최종 결과 리포트 ")
    print("=" * 70)
    for platform, count in stats.items():
        print(f"  • {platform.ljust(10)}: {count:>4} 건 수집 완료")
    print("-" * 70)
    print(f"  총 신규/갱신 공고 : {total_collected} 건")
    print(f"  자동 마감 처리     : {closed_count} 건")
    print(f"  총 소요 시간       : {elapsed} 초")
    print("=" * 70)


if __name__ == "__main__":
    main()
