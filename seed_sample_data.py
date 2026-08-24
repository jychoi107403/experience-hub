# ==============================================================================
# 파일명: seed_sample_data.py
# 설명: Supabase DB 연결을 검증하고 즉시 웹 화면에서 볼 수 있는 테스트용
#       체험단 샘플 데이터를 주입(Insert/Upsert)하는 유틸리티 스크립트
# 실행 방법: python seed_sample_data.py
# ==============================================================================

import os
import sys
from datetime import datetime, timedelta, timezone

# Windows 콘솔 한글/이모지 인코딩 지원
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 풍부한 체험단 테스트 데이터 생성
now = datetime.now(timezone.utc)
sample_campaigns = [
    {
        "platform": "레뷰",
        "title": "[강남/역삼] 정통 이탈리안 파스타 & 화덕피자 2인 코스 식사권",
        "original_url": "https://www.revu.net/campaign/sample-01",
        "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&auto=format&fit=crop&q=80",
        "category": "맛집",
        "media_type": "블로그",
        "location": "서울 강남구",
        "reward": "5만원 상당 식사권 (파스타 1종 + 피자 1종 + 에이드 2잔)",
        "capacity": 10,
        "applied_count": 42,
        "end_date": (now + timedelta(days=5)).isoformat(),
        "is_closed": False
    },
    {
        "platform": "강남맛집",
        "title": "[홍대/연남] 감성 브런치 & 드립커피 디저트 세트",
        "original_url": "https://xn--939au0g4vj8sq.net/campaign/sample-02",
        "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=600&auto=format&fit=crop&q=80",
        "category": "맛집",
        "media_type": "인스타그램",
        "location": "서울 마포구",
        "reward": "프렌치토스트 + 시그니처 커피 2잔 제공",
        "capacity": 15,
        "applied_count": 89,
        "end_date": (now + timedelta(days=3)).isoformat(),
        "is_closed": False
    },
    {
        "platform": "디너의여왕",
        "title": "[제주/애월] 오션뷰 감성 독채 펜션 1박 숙박권",
        "original_url": "https://dinnerqueen.net/taste/sample-03",
        "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=600&auto=format&fit=crop&q=80",
        "category": "숙박/여행",
        "media_type": "블로그",
        "location": "제주 제주시",
        "reward": "주중 1박 무료 숙박권 (최대 4인 기준, 바베큐 포함)",
        "capacity": 3,
        "applied_count": 128,
        "end_date": (now + timedelta(days=7)).isoformat(),
        "is_closed": False
    },
    {
        "platform": "레뷰",
        "title": "[프리미엄 뷰티] 저자극 수분 진정 세럼 본품 100ml 증정",
        "original_url": "https://www.revu.net/campaign/sample-04",
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80",
        "category": "뷰티/미용",
        "media_type": "릴스/숏츠",
        "location": "전국(배송형)",
        "reward": "세럼 본품 1개 (소비자가 45,000원 상당)",
        "capacity": 30,
        "applied_count": 210,
        "end_date": (now + timedelta(days=2)).isoformat(),
        "is_closed": False
    },
    {
        "platform": "미블",
        "title": "[수원/인계동] 1:1 맞춤 프리미엄 헤어 클리닉 & 커트",
        "original_url": "https://mrblog.net/campaign/sample-05",
        "image_url": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600&auto=format&fit=crop&q=80",
        "category": "뷰티/미용",
        "media_type": "블로그",
        "location": "경기 수원시",
        "reward": "헤어 단백질 클리닉 + 디자인 커트 시술",
        "capacity": 5,
        "applied_count": 19,
        "end_date": (now + timedelta(days=4)).isoformat(),
        "is_closed": False
    },
    {
        "platform": "리뷰노트",
        "title": "[홈카페/식품] 최고급 스페셜티 원두 200g 2종 세트",
        "original_url": "https://www.reviewnote.co.kr/campaign/sample-06",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
        "category": "생활/식품",
        "media_type": "블로그",
        "location": "전국(배송형)",
        "reward": "원두 2종 세트 무료 배송",
        "capacity": 20,
        "applied_count": 65,
        "end_date": (now + timedelta(days=6)).isoformat(),
        "is_closed": False
    }
]


def seed_data():
    print("=" * 60)
    print(" [테스트] Supabase 연동 확인 및 샘플 데이터 주입 시작 ")
    print("=" * 60)

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n[안내] .env 파일에 SUPABASE_URL 및 SUPABASE_KEY가 아직 설정되지 않았습니다.")
        print("💡 .env.example 파일을 복사하여 .env 파일을 생성하고 실제 키를 넣어주세요.")
        return

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[성공] Supabase 클라이언트 연결 성공!")

        print(f"총 {len(sample_campaigns)}건의 테스트 캠페인 데이터 Upsert 시도 중...")
        res = supabase.table("campaigns").upsert(sample_campaigns, on_conflict="original_url").execute()

        print(f"[완료] {len(res.data)}건의 캠페인이 Supabase 'campaigns' 테이블에 저장되었습니다.")
        print("👉 Supabase Dashboard > Table Editor에서 저장된 데이터를 확인해보세요!")

    except Exception as e:
        print(f"\n[오류] DB 저장 실패: {e}")
        print("💡 1단계의 SQL 마이그레이션(001_create_campaigns_table.sql)을 Supabase SQL Editor에서 실행했는지 확인해주세요.")


if __name__ == "__main__":
    seed_data()
