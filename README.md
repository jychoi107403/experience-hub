# 🎁 국내 체험단 통합 모음 서비스 (Experience Hub)

여러 국내 체험단 플랫폼(디너의여왕, 클라우드리뷰, 리뷰노트, 레뷰 등)에 흩어져 있는 **1,100건 이상의 체험단 모집 공고를 한곳에서 쉽고 빠르게 검색하고 모아보는 24시간 무인 자동화 웹 서비스**입니다.

---

## 📁 프로젝트 폴더 구조

```text
experience-hub/
├── README.md                          # 프로젝트 종합 가이드
├── DEPLOY_GUIDE.md                    # 🚀 GitHub / Supabase / Cloudflare 배포 가이드
├── auto_scheduler.py                  # 🤖 로컬 24시간 무인 자동 수집기 (4시간 주기)
├── requirements.txt                   # 파이썬 필수 패키지 목록
├── .env.example                       # 환경변수(Supabase DB 키) 템플릿
├── .gitignore                         # Git 제외 설정 (보안 키 보호)
├── main.py                            # 크롤러 메인 일괄 실행기 (1,169건 수집)
├── seed_sample_data.py                # Supabase 연결 및 테스트 데이터 주입기
├── .github/
│   └── workflows/
│       └── crawler.yml                # ⏰ 24시간 자동 실행 스케줄러 (매 6시간마다)
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py                # 공통 베이스 크롤러 (배치 Upsert, 마감 자동정리)
│   ├── dinnerqueen_crawler.py         # 디너의여왕 크롤러 (120건 실제 매장 사진/신청수)
│   ├── cloudreview_crawler.py         # 클라우드리뷰 크롤러 (1,049건 전수 수집)
│   ├── reviewnote_crawler.py          # 리뷰노트 크롤러
│   ├── revu_crawler.py                # 레뷰 크롤러
│   └── gangnam_crawler.py             # 강남맛집 크롤러
├── supabase/
│   └── migrations/
│       └── 001_create_campaigns_table.sql  # 1단계 DB 테이블 생성 쿼리
└── web/
    ├── index.html                     # 모던 웹 대시보드 HTML
    ├── app.js                         # React 기반 필터/검색/경쟁률/당첨확률순 UI 로직
    ├── style.css                      # 반응형 및 세련된 카드 스타일
    └── serve.py                       # 원클릭 로컬 웹 서버 실행기
```

---

## 🤖 24시간 완전 무인 자동 수집 시스템 동작 방식

1. **클라우드 자동화 (GitHub Actions)**:
   - 사용자가 컴퓨터를 꺼두어도 GitHub 클라우드 서버가 **하루 4회 (00:00, 06:00, 12:00, 18:00 KST)** 마다 알아서 1,169건의 공고를 긁어오고 마감된 공고를 정리합니다.
2. **로컬 자동화 (선택 사항)**:
   - 내 컴퓨터에서 직접 자동으로 돌리고 싶을 때는 `python auto_scheduler.py` 만 켜두시면 4시간마다 알아서 무한 반복 수집합니다.
