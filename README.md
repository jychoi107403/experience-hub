# 🎁 국내 체험단 통합 모음 서비스 (Experience Hub)

여러 국내 체험단 플랫폼(레뷰, 강남맛집, 디너의여왕, 미블 등)에 흩어져 있는 체험단 모집 공고를 한곳에서 쉽고 빠르게 검색하고 모아보는 웹 서비스 프로젝트입니다.

---

## 📁 프로젝트 폴더 구조

```text
experience-hub/
├── README.md                          # 프로젝트 종합 가이드
├── DEPLOY_GUIDE.md                    # 🚀 GitHub / Supabase / Cloudflare 배포 가이드
├── requirements.txt                   # 파이썬 필수 패키지 목록
├── .env.example                       # 환경변수(Supabase DB 키) 템플릿
├── .gitignore                         # Git 제외 설정 (보안 키 보호)
├── main.py                            # 크롤러 메인 일괄 실행기
├── seed_sample_data.py                # Supabase 연결 및 테스트 데이터 주입기
├── .github/
│   └── workflows/
│       └── crawler.yml                # ⏰ 매일 자동 실행되는 GitHub Actions 워크플로우
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py                # 공통 베이스 크롤러 (Upsert, Rate Limiting)
│   ├── dinnerqueen_crawler.py         # 디너의여왕(DinnerQueen) 크롤러
│   ├── revu_crawler.py                # 레뷰(Revu) 크롤러
│   └── gangnam_crawler.py             # 강남맛집 크롤러
├── supabase/
│   └── migrations/
│       └── 001_create_campaigns_table.sql  # 1단계 DB 테이블 생성 쿼리
└── web/
    ├── index.html                     # 모던 웹 대시보드 HTML
    ├── app.js                         # React 기반 필터/검색/D-Day/찜 UI 로직
    ├── style.css                      # 반응형 및 세련된 카드 스타일
    └── serve.py                       # 원클릭 로컬 웹 서버 실행기
```

---

## 🚀 배포 및 자동화 가이드 (GitHub & Cloudflare Pages)

자세한 배포 및 연동 방법은 **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** 문서를 참고하세요!

1. **GitHub 저장소에 코드 업로드**: `git init` -> `git add .` -> `git commit` -> `git push`
2. **GitHub Actions 크롤러 자동화**: 매일 오전 6시/오후 6시에 GitHub 클라우드에서 자동으로 크롤링되어 Supabase DB 갱신
3. **Cloudflare Pages 무료 웹 배포**: `web` 폴더를 루트로 설정하여 전 세계에 무료 웹 호스팅 배포
