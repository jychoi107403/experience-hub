# ==============================================================================
# 파일명: auto_scheduler.py
# 설명: 로컬 컴퓨터에서 백그라운드로 켜두면 지정된 주기(예: 4시간)마다
#       자동으로 1,169건 이상의 최신 체험단을 수집하고 마감 공고를 정리하는 자동 스케줄러
# 실행 방법: python auto_scheduler.py
# ==============================================================================

import sys
import time
from datetime import datetime

# Windows 콘솔 인코딩 대응
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from main import main as run_crawler_main

# 자동 수집 주기 설정 (초 단위: 4시간 = 14400초, 테스트는 3600초 등 조절 가능)
INTERVAL_HOURS = 4
INTERVAL_SECONDS = INTERVAL_HOURS * 3600


def run_forever():
    print("=" * 70)
    print(" 🤖 [Experience Hub] 24시간 완전 무인 자동 크롤링 스케줄러 가동 ")
    print("=" * 70)
    print(f"⏰ 자동 실행 주기: {INTERVAL_HOURS}시간마다 1회씩 무한 자동 실행")
    print("💡 이 창을 켜두시면 알아서 최신 공고를 24시간 수집합니다.")
    print("💡 종료하려면 언제든 터미널에서 Ctrl + C 를 누르세요.")
    print("=" * 70)

    round_count = 1
    while True:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🚀 [제 {round_count}회차 자동 수집 시작] 실행 일시: {now_str}")
        
        try:
            # 메인 크롤러 실행
            run_crawler_main()
            print(f"\n✅ [제 {round_count}회차 수집 성공 완료!]")
        except Exception as e:
            print(f"\n❌ [오류 발생]: {e}")

        round_count += 1
        print(f"\n💤 다음 자동 수집까지 {INTERVAL_HOURS}시간 동안 대기합니다...")
        
        # 지정된 시간 동안 대기
        try:
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n👋 자동 스케줄러를 안전하게 종료했습니다.")
            break


if __name__ == "__main__":
    run_forever()
