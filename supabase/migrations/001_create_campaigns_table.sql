-- ==============================================================================
-- 파일명: 001_create_campaigns_table.sql
-- 설명: 국내 체험단 모음 사이트의 핵심 캠페인 데이터를 저장하기 위한 테이블 생성 스크립트
-- 적용 위치: Supabase Dashboard > SQL Editor에 복사하여 실행
-- ==============================================================================

-- 1. campaigns (체험단 캠페인) 테이블 생성
-- 만약 기존에 동일한 이름의 테이블이 있다면 생성하지 않습니다.
CREATE TABLE IF NOT EXISTS public.campaigns (
    -- 고유 식별자 (UUID 형태로 자동 생성)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 체험단 플랫폼 이름 (예: '레뷰', '강남맛집', '디너의여왕', '미블' 등)
    platform VARCHAR(50) NOT NULL,

    -- 해당 플랫폼 내의 고유 캠페인 ID 또는 코드 (선택 사항)
    platform_id VARCHAR(100),

    -- 체험단 캠페인 제목 (예: '[강남] 맛있는 파스타 전문점 2인 식사권')
    title VARCHAR(255) NOT NULL,

    -- 원본 사이트의 상세 페이지 URL (중복 수집 방지를 위해 고유값 UNIQUE 설정)
    original_url TEXT NOT NULL UNIQUE,

    -- 대표 썸네일 이미지 URL
    image_url TEXT,

    -- 카테고리 분류 (예: '맛집', '뷰티/미용', '숙박/여행', '생활/식품', '디지털/가전' 등)
    category VARCHAR(50) NOT NULL,

    -- 리뷰 매체 (예: '블로그', '인스타그램', '유튜브', '릴스/숏츠', '기타')
    media_type VARCHAR(50) DEFAULT '블로그',

    -- 제공 지역 (예: '서울 강남구', '경기 수원시', '전국(배송형)' 등)
    location VARCHAR(100),

    -- 제공 혜택 및 제품 (예: '파스타+피자 2인 세트 제공 (5만원 상당)')
    reward TEXT,

    -- 모집 인원 (예: 10)
    capacity INTEGER DEFAULT 0,

    -- 현재 신청 인원 (예: 35)
    applied_count INTEGER DEFAULT 0,

    -- 모집 마감 일시 (타임존 포함 일시)
    end_date TIMESTAMPTZ,

    -- 모집 마감 여부 (true: 마감됨, false: 모집중)
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,

    -- 데이터 최초 수집/등록 일시
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- 데이터 최근 수정/갱신 일시
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 테이블 설명 코멘트 추가
COMMENT ON TABLE public.campaigns IS '국내 다양한 플랫폼의 체험단 모집 캠페인 통합 저장 테이블';
COMMENT ON COLUMN public.campaigns.platform IS '체험단 플랫폼명 (레뷰, 강남맛집 등)';
COMMENT ON COLUMN public.campaigns.original_url IS '원본 상세 링크 (중복 수집 방지 기준)';
COMMENT ON COLUMN public.campaigns.is_closed IS '모집 마감 여부';

-- ==============================================================================
-- 2. 검색 및 필터링 속도 향상을 위한 인덱스(Index) 생성
-- 데이터가 수만 건으로 늘어나도 빠르게 조회할 수 있도록 도와줍니다.
-- ==============================================================================

-- 플랫폼별 필터링 인덱스
CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON public.campaigns (platform);

-- 카테고리별 필터링 인덱스
CREATE INDEX IF NOT EXISTS idx_campaigns_category ON public.campaigns (category);

-- 지역별 필터링 인덱스
CREATE INDEX IF NOT EXISTS idx_campaigns_location ON public.campaigns (location);

-- 모집 마감일 정렬 및 마감 여부 필터링용 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_campaigns_status_end_date ON public.campaigns (is_closed, end_date ASC);

-- 등록일자 최신순 정렬용 인덱스
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON public.campaigns (created_at DESC);

-- ==============================================================================
-- 3. 데이터 수정 시 updated_at 컬럼 자동 갱신 트리거(Trigger) 함수
-- ==============================================================================

-- updated_at 시간을 현재 시간(now())으로 바꿔주는 함수 정의
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- campaigns 테이블에 UPDATE가 발생할 때마다 위 함수를 자동 실행하도록 트리거 연결
DROP TRIGGER IF EXISTS trg_campaigns_updated_at ON public.campaigns;
CREATE TRIGGER trg_campaigns_updated_at
    BEFORE UPDATE ON public.campaigns
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- ==============================================================================
-- 4. 보안 및 권한 설정 (Row Level Security - RLS)
-- 일반 방문자(웹사이트 사용자)는 데이터를 '조회(SELECT)'만 할 수 있도록 설정합니다.
-- ==============================================================================

-- RLS 활성화
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;

-- 기존 정책이 있다면 삭제 후 재생성
DROP POLICY IF EXISTS "누구나 체험단 목록을 조회할 수 있음" ON public.campaigns;

-- 누구나(익명 사용자 포함) 체험단 목록을 읽을 수 있도록 허용하는 정책
CREATE POLICY "누구나 체험단 목록을 조회할 수 있음"
    ON public.campaigns
    FOR SELECT
    TO anon, authenticated
    USING (true);
