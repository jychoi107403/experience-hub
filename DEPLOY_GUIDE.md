# 🚀 GitHub, Supabase, Cloudflare Pages 완벽 연동 & 배포 가이드

이 문서는 초보자분들도 쉽게 따라 하실 수 있도록 **1) GitHub에 코드 올리기**, **2) GitHub Actions 자동 크롤러 세팅하기**, **3) Cloudflare Pages 무료 웹 배포하기**를 순서대로 안내합니다.

---

## 1단계: GitHub에 소스 코드 올리기 (Git Push)

터미널(PowerShell 또는 명령 프롬프트)을 열고 프로젝트 폴더(`experience-hub`)에서 아래 명령어를 순서대로 실행합니다:

```bash
# 1. 프로젝트 폴더로 이동 (이미 해당 폴더인 경우 생략 가능)
cd C:\Users\user\.gemini\antigravity\scratch\experience-hub

# 2. Git 초기화
git init

# 3. 모든 파일 추가 (.env 파일은 .gitignore 덕분에 자동으로 제외되니 안심하세요!)
git add .

# 4. 첫 커밋 생성
git commit -m "feat: 국내 체험단 통합 모음 사이트 및 자동 크롤러 완성"

# 5. 기본 브랜치 이름을 main으로 변경
git branch -M main

# 6. 본인의 GitHub 원격 저장소 주소 연결 (아래 URL을 본인의 실제 GitHub 저장소 URL로 변경하세요)
git remote add origin https://github.com/본인아이디/저장소이름.git

# 7. GitHub로 업로드
git push -u origin main
```

---

## 2단계: GitHub Actions 크롤러에 Supabase 비밀 키 등록하기

GitHub에서 크롤러가 매일 자동으로 돌아갈 때 Supabase DB에 접속할 수 있도록 **비밀 키(Secrets)**를 등록해야 합니다.

1. 본인의 **GitHub 저장소 페이지**로 이동합니다.
2. 상단 탭에서 **`Settings`** (설정)를 클릭합니다.
3. 왼쪽 사이드바 메뉴에서 **`Secrets and variables`** > **`Actions`** 를 클릭합니다.
4. 초록색 **`New repository secret`** 버튼을 누르고 아래 2개의 비밀 값을 각각 추가합니다:

| Name (이름) | Secret Value (값) | 설명 |
| :--- | :--- | :--- |
| **`SUPABASE_URL`** | `https://내프로젝트ID.supabase.co` | Supabase 대시보드 > Project Settings > API에서 확인 |
| **`SUPABASE_KEY`** | `eyJhbGciOi... (service_role 키)` | Supabase의 `service_role (secret)` 키 입력 |

> [!TIP]
> **크롤러 수동 실행 테스트해보기**:
> 1. GitHub 저장소 상단의 **`Actions`** 탭을 클릭합니다.
> 2. 왼쪽 목록에서 **`Experience Hub Crawler`** 를 클릭합니다.
> 3. 우측의 **`Run workflow`** 버튼을 누르면 지금 즉시 GitHub의 무료 클라우드 서버에서 크롤러가 돌아가며 Supabase에 데이터를 수집/적재합니다!

---

## 3단계: Cloudflare Pages로 무료 웹 사이트 배포하기

전 세계 어디서나 빠른 속도로 접속할 수 있는 무료 웹 호스팅 서비스인 **Cloudflare Pages**에 사이트를 배포합니다.

### 1. Cloudflare Pages 프로젝트 생성
1. [Cloudflare 대시보드(dash.cloudflare.com)](https://dash.cloudflare.com)에 로그인합니다.
2. 왼쪽 메뉴에서 **`Workers & Pages`** (또는 `Pages`)를 클릭합니다.
3. **`Create application`** > **`Pages`** 탭 선택 > **`Connect to Git`** (Git에 연결)을 클릭합니다.
4. 방금 코드를 올린 **GitHub 저장소**를 선택하고 **`Begin setup`** 을 누릅니다.

### 2. 빌드 및 배포 설정 (중요!)
설정 화면에서 아래와 같이 입력합니다:
- **Project name (프로젝트 이름)**: `experience-hub` (원하는 이름)
- **Production branch**: `main`
- **Framework preset**: `None` (없음)
- **Build command (빌드 명령어)**: *(비워둡니다)*
- **Build output directory (빌드 출력 디렉터리)**: `web` ⭐ (반드시 `web`으로 입력)

### 3. 배포 완료!
- 맨 아래 **`Save and Deploy`** (저장 및 배포) 버튼을 클릭합니다.
- 약 30초 후 **`https://experience-hub.pages.dev`** 와 같은 나만의 무료 웹사이트 주소가 생성됩니다!

---

## 4단계: 배포된 웹 사이트에 Supabase 실시간 연동하기

Cloudflare Pages에 배포된 웹 화면에서 Supabase의 실제 데이터를 바로 조회하려면:
1. [`web/app.js`](file:///C:/Users/user/.gemini/antigravity/scratch/experience-hub/web/app.js) 상단의 `SUPABASE_URL`과 `SUPABASE_ANON_KEY` 부분에 본인의 Supabase **`Project URL`** 및 **`anon (public)` 키**를 적어줍니다.
2. 수정 후 `git add web/app.js` -> `git commit -m "fix: Supabase client key"` -> `git push origin main` 을 실행하면 Cloudflare Pages가 변경 사항을 감지하여 10초 만에 자동 재배포합니다!
