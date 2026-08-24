// ==============================================================================
// 파일명: web/app.js
// 설명: 국내 체험단 통합 모음 사이트(Experience Hub)의 React 프론트엔드 핵심 로직
// 주요 기능: 실시간 필터링/검색, D-Day 계산, 북마크(찜), Supabase 연동 및 Fallback
// ==============================================================================

const { useState, useEffect, useMemo } = React;

// 1. Supabase 접속 설정 (본인의 Supabase 키가 있다면 여기에 입력하세요)
// 입력하지 않아도 아래 MOCK_CAMPAIGNS 데이터로 즉시 완벽히 동작합니다!
const SUPABASE_URL = "https://bmosdfsnecapqkrnibyn.supabase.co";  // 예: "https://xxxx.supabase.co"
const SUPABASE_ANON_KEY = "sb_publishable_HVzgvqHrVIJjUFDByiZPUQ_P6hExwWo"; // 예: "eyJhbGciOi..."

// 2. 기본 고품질 샘플 데이터 (Supabase 미연동 시 자동 로드)
const MOCK_CAMPAIGNS = [
    {
        id: "mock-1",
        platform: "디너의여왕",
        title: "[강남/신사] 정통 일식 오마카세 디너 2인 코스 체험권",
        original_url: "https://dinnerqueen.net/taste",
        image_url: "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600&auto=format&fit=crop&q=80",
        category: "맛집",
        media_type: "블로그",
        location: "서울 강남구",
        reward: "오마카세 디너 2인 (18만원 상당)",
        capacity: 5,
        applied_count: 38,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString(), // D-2
        is_closed: false
    },
    {
        id: "mock-2",
        platform: "레뷰",
        title: "[홍대/연남] 감성 브런치 플레이트 & 수제 에이드 2잔",
        original_url: "https://www.revu.net",
        image_url: "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=600&auto=format&fit=crop&q=80",
        category: "맛집",
        media_type: "인스타그램",
        location: "서울 마포구",
        reward: "브런치 세트 (5만원 상당 식사권)",
        capacity: 10,
        applied_count: 52,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 4).toISOString(), // D-4
        is_closed: false
    },
    {
        id: "mock-3",
        platform: "디너의여왕",
        title: "[제주/애월] 오션뷰 감성 독채 풀빌라 1박 무료 숙박권",
        original_url: "https://dinnerqueen.net/taste",
        image_url: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=600&auto=format&fit=crop&q=80",
        category: "숙박/여행",
        media_type: "블로그",
        location: "제주 제주시",
        reward: "주중 독채 1박 (최대 4인 바베큐 무료)",
        capacity: 3,
        applied_count: 145,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 1).toISOString(), // D-1
        is_closed: false
    },
    {
        id: "mock-4",
        platform: "강남맛집",
        title: "[성수/뚝섬] 숙성 한우 1++ 구이 & 된장찌개 2인 세트",
        original_url: "https://xn--939au0g4vj8sq.net",
        image_url: "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80",
        category: "맛집",
        media_type: "블로그",
        location: "서울 성동구",
        reward: "한우 모듬 300g + 식사류 제공",
        capacity: 8,
        applied_count: 67,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3).toISOString(), // D-3
        is_closed: false
    },
    {
        id: "mock-5",
        platform: "레뷰",
        title: "[스킨케어] 고농축 히알루론산 수분 앰플 본품 50ml",
        original_url: "https://www.revu.net",
        image_url: "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80",
        category: "뷰티/미용",
        media_type: "릴스/숏츠",
        location: "전국(배송형)",
        reward: "앰플 본품 1개 (소비자가 42,000원)",
        capacity: 50,
        applied_count: 320,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 6).toISOString(), // D-6
        is_closed: false
    },
    {
        id: "mock-6",
        platform: "미블",
        title: "[수원/인계동] 프리미엄 헤어 스파 & 두피 케어 패키지",
        original_url: "https://mrblog.net",
        image_url: "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600&auto=format&fit=crop&q=80",
        category: "뷰티/미용",
        media_type: "블로그",
        location: "경기 수원시",
        reward: "헤드스파 + 커트 시술 (8만원 상당)",
        capacity: 5,
        applied_count: 24,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 5).toISOString(), // D-5
        is_closed: false
    },
    {
        id: "mock-7",
        platform: "리뷰노트",
        title: "[홈카페] 에티오피아 예가체프 스페셜티 드립백 20개입",
        original_url: "https://www.reviewnote.co.kr",
        image_url: "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
        category: "생활/식품",
        media_type: "블로그",
        location: "전국(배송형)",
        reward: "드립백 선물세트 무료 배송",
        capacity: 30,
        applied_count: 88,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString(), // D-7
        is_closed: false
    },
    {
        id: "mock-8",
        platform: "강남맛집",
        title: "[부산/해운대] 광안대교 뷰 루프탑 펍 & 수제맥주 피맥 세트",
        original_url: "https://xn--939au0g4vj8sq.net",
        image_url: "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=600&auto=format&fit=crop&q=80",
        category: "맛집",
        media_type: "인스타그램",
        location: "부산 해운대구",
        reward: "시그니처 피자 + 수제맥주 2잔",
        capacity: 6,
        applied_count: 41,
        end_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3).toISOString(),
        is_closed: false
    }
];

// 카테고리 목록 정의
const CATEGORIES = [
    { id: "all", name: "전체", icon: "fa-border-all" },
    { id: "맛집", name: "맛집/카페", icon: "fa-utensils" },
    { id: "뷰티/미용", name: "뷰티/미용", icon: "fa-wand-magic-sparkles" },
    { id: "숙박/여행", name: "숙박/여행", icon: "fa-plane" },
    { id: "생활/식품", name: "생활/식품", icon: "fa-basket-shopping" },
    { id: "디지털/가전", name: "디지털/가전", icon: "fa-laptop" },
];

// 플랫폼 목록 정의
const PLATFORMS = ["전체", "레뷰", "강남맛집", "디너의여왕", "미블", "리뷰노트"];

// 지역 필터 목록 정의
const LOCATIONS = ["전체 지역", "서울", "경기", "인천", "부산", "제주", "전국(배송형)"];

// 플랫폼별 뱃지 스타일 매핑 함수
function getPlatformBadge(platform) {
    switch (platform) {
        case "레뷰":
            return { bg: "bg-red-50 text-red-600 border-red-200", icon: "fa-r" };
        case "디너의여왕":
            return { bg: "bg-purple-50 text-purple-600 border-purple-200", icon: "fa-crown" };
        case "강남맛집":
            return { bg: "bg-blue-50 text-blue-600 border-blue-200", icon: "fa-utensils" };
        case "미블":
            return { bg: "bg-emerald-50 text-emerald-600 border-emerald-200", icon: "fa-leaf" };
        case "리뷰노트":
            return { bg: "bg-amber-50 text-amber-700 border-amber-200", icon: "fa-book-open" };
        default:
            return { bg: "bg-slate-100 text-slate-700 border-slate-200", icon: "fa-tag" };
    }
}

// 리뷰 매체 뱃지 매핑 함수
function getMediaBadge(mediaType) {
    switch (mediaType) {
        case "블로그":
            return "bg-emerald-100 text-emerald-800";
        case "인스타그램":
            return "bg-pink-100 text-pink-700";
        case "릴스/숏츠":
            return "bg-rose-100 text-rose-700";
        case "유튜브":
            return "bg-red-100 text-red-800";
        default:
            return "bg-slate-100 text-slate-700";
    }
}

// D-Day 계산 헬퍼 함수
function getDDay(endDateString) {
    if (!endDateString) return { text: "상시모집", isUrgent: false };
    const diffTime = new Date(endDateString) - new Date();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return { text: "마감", isUrgent: false, isClosed: true };
    if (diffDays === 0) return { text: "오늘마감", isUrgent: true };
    if (diffDays <= 3) return { text: `D-${diffDays}`, isUrgent: true };
    return { text: `D-${diffDays}`, isUrgent: false };
}


// ==============================================================================
// 메인 App 컴포넌트
// ==============================================================================
function App() {
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedPlatform, setSelectedPlatform] = useState("전체");
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [selectedLocation, setSelectedLocation] = useState("전체 지역");
    const [selectedMedia, setSelectedMedia] = useState("전체");
    const [sortBy, setSortBy] = useState("end_date_asc"); // end_date_asc, created_desc, applied_desc
    const [bookmarks, setBookmarks] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem("experience_hub_bookmarks") || "[]");
        } catch {
            return [];
        }
    });
    const [showOnlyBookmarks, setShowOnlyBookmarks] = useState(false);
    const [isSupabaseConnected, setIsSupabaseConnected] = useState(false);

    // 1. 데이터 로드 (Supabase 또는 Fallback Mock)
    useEffect(() => {
        async function fetchCampaigns() {
            setLoading(true);
            if (SUPABASE_URL && SUPABASE_ANON_KEY && window.supabase) {
                try {
                    const client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
                    const { data, error } = await client
                        .from("campaigns")
                        .select("*")
                        .eq("is_closed", false)
                        .order("created_at", { ascending: false });

                    if (!error && data && data.length > 0) {
                        setCampaigns(data);
                        setIsSupabaseConnected(true);
                        setLoading(false);
                        return;
                    }
                } catch (e) {
                    console.warn("Supabase 연결 실패, 기본 샘플 데이터로 대체합니다:", e);
                }
            }
            // Supabase 미연동 시 기본 Mock 데이터 사용
            setCampaigns(MOCK_CAMPAIGNS);
            setLoading(false);
        }
        fetchCampaigns();
    }, []);

    // 2. 북마크 토글 함수
    const toggleBookmark = (id, e) => {
        e.preventDefault();
        e.stopPropagation();
        setBookmarks(prev => {
            const next = prev.includes(id) ? prev.filter(bId => bId !== id) : [...prev, id];
            localStorage.setItem("experience_hub_bookmarks", JSON.stringify(next));
            return next;
        });
    };

    // 3. 필터링 및 정렬 연산
    const filteredCampaigns = useMemo(() => {
        return campaigns.filter(c => {
            // 북마크 전용 보기 필터
            if (showOnlyBookmarks && !bookmarks.includes(c.id)) {
                return false;
            }

            // 검색어 필터 (제목, 지역, 제공내역)
            if (searchTerm.trim()) {
                const term = searchTerm.toLowerCase();
                const matchTitle = (c.title || "").toLowerCase().includes(term);
                const matchLocation = (c.location || "").toLowerCase().includes(term);
                const matchReward = (c.reward || "").toLowerCase().includes(term);
                if (!matchTitle && !matchLocation && !matchReward) return false;
            }

            // 플랫폼 필터
            if (selectedPlatform !== "전체" && c.platform !== selectedPlatform) {
                return false;
            }

            // 카테고리 필터
            if (selectedCategory !== "all" && !c.category.includes(selectedCategory)) {
                return false;
            }

            // 지역 필터
            if (selectedLocation !== "전체 지역") {
                if (selectedLocation === "전국(배송형)" && !c.location.includes("배송")) return false;
                if (selectedLocation !== "전국(배송형)" && !c.location.includes(selectedLocation)) return false;
            }

            // 미디어 필터
            if (selectedMedia !== "전체" && c.media_type !== selectedMedia) {
                return false;
            }

            return true;
        }).sort((a, b) => {
            if (sortBy === "end_date_asc") {
                const dateA = a.end_date ? new Date(a.end_date) : new Date(9999, 11, 31);
                const dateB = b.end_date ? new Date(b.end_date) : new Date(9999, 11, 31);
                return dateA - dateB;
            }
            if (sortBy === "applied_desc") {
                return (b.applied_count || 0) - (a.applied_count || 0);
            }
            // created_desc 기본
            return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        });
    }, [campaigns, searchTerm, selectedPlatform, selectedCategory, selectedLocation, selectedMedia, sortBy, bookmarks, showOnlyBookmarks]);

    return (
        <div className="min-h-screen flex flex-col bg-slate-50">
            {/* 상단 글래스모피즘 네비게이션 */}
            <header className="sticky top-0 z-40 glass-nav">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center space-x-3 cursor-pointer" onClick={() => { setSelectedCategory("all"); setSelectedPlatform("전체"); setShowOnlyBookmarks(false); }}>
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-rose-500 flex items-center justify-center text-white shadow-md">
                            <i className="fa-solid fa-gift text-lg"></i>
                        </div>
                        <div>
                            <span className="text-xl font-extrabold bg-gradient-to-r from-indigo-600 to-rose-500 bg-clip-text text-transparent">
                                체험단 모아
                            </span>
                            <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                                Experience Hub
                            </span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-3">
                        {/* 찜한 목록 필터 토글 버튼 */}
                        <button
                            onClick={() => setShowOnlyBookmarks(!showOnlyBookmarks)}
                            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                                showOnlyBookmarks
                                    ? "bg-rose-500 text-white shadow-sm"
                                    : "bg-slate-100 hover:bg-slate-200 text-slate-700"
                            }`}
                        >
                            <i className={`fa-heart ${showOnlyBookmarks ? "fa-solid text-white" : "fa-regular text-rose-500"}`}></i>
                            <span>찜한 목록 ({bookmarks.length})</span>
                        </button>

                        {/* 연동 상태 뱃지 */}
                        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
                            <span className={`w-2 h-2 rounded-full ${isSupabaseConnected ? "bg-emerald-500" : "bg-amber-400"}`}></span>
                            <span>{isSupabaseConnected ? "Supabase 연동됨" : "체험/로컬 모드"}</span>
                        </div>
                    </div>
                </div>
            </header>

            {/* 메인 히어로 배너 & 검색창 */}
            <section className="bg-gradient-to-b from-indigo-900 via-slate-900 to-slate-900 text-white py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-4xl mx-auto text-center space-y-4">
                    <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
                        국내 모든 체험단을 <span className="text-rose-400">한곳에서</span> 스마트하게!
                    </h1>
                    <p className="text-slate-300 text-sm sm:text-base max-w-2xl mx-auto">
                        레뷰, 디너의여왕, 강남맛집, 미블 등 흩어져 있는 맛집·뷰티·숙박 체험단을 검색하고 마감 전 바로 신청하세요.
                    </p>

                    {/* 통합 검색바 */}
                    <div className="relative max-w-2xl mx-auto pt-2">
                        <div className="relative flex items-center">
                            <i className="fa-solid fa-magnifying-glass absolute left-4 text-slate-400"></i>
                            <input
                                type="text"
                                placeholder="지역(강남, 홍대, 제주) 또는 키워드(오마카세, 세럼, 카페)를 검색해보세요"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-11 pr-10 py-3.5 rounded-2xl bg-white/95 text-slate-800 placeholder-slate-400 text-sm sm:text-base shadow-xl focus:outline-none focus:ring-4 focus:ring-indigo-400/50"
                            />
                            {searchTerm && (
                                <button
                                    onClick={() => setSearchTerm("")}
                                    className="absolute right-3 w-6 h-6 rounded-full bg-slate-200 text-slate-600 hover:bg-slate-300 flex items-center justify-center text-xs"
                                >
                                    <i className="fa-solid fa-xmark"></i>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            {/* 필터 및 컨트롤 바 */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">
                
                {/* 1. 카테고리 칩 목록 */}
                <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
                    {CATEGORIES.map(cat => (
                        <button
                            key={cat.id}
                            onClick={() => setSelectedCategory(cat.id)}
                            className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
                                selectedCategory === cat.id
                                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-200 scale-105"
                                    : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                            }`}
                        >
                            <i className={`fa-solid ${cat.icon}`}></i>
                            <span>{cat.name}</span>
                        </button>
                    ))}
                </div>

                {/* 2. 세부 필터 (플랫폼 탭, 지역, 미디어, 정렬) */}
                <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-4">
                    {/* 플랫폼 선택 탭 */}
                    <div className="flex items-center flex-wrap gap-2">
                        <span className="text-xs font-bold text-slate-400 mr-2 uppercase tracking-wider">플랫폼:</span>
                        {PLATFORMS.map(p => (
                            <button
                                key={p}
                                onClick={() => setSelectedPlatform(p)}
                                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                                    selectedPlatform === p
                                        ? "bg-slate-900 text-white"
                                        : "bg-slate-100 hover:bg-slate-200 text-slate-600"
                                }`}
                            >
                                {p}
                            </button>
                        ))}
                    </div>

                    <div className="border-t border-slate-100 pt-3 flex flex-wrap items-center justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-2">
                            {/* 지역 선택 */}
                            <select
                                value={selectedLocation}
                                onChange={(e) => setSelectedLocation(e.target.value)}
                                className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                                {LOCATIONS.map(loc => (
                                    <option key={loc} value={loc}>{loc}</option>
                                ))}
                            </select>

                            {/* 매체 선택 */}
                            <select
                                value={selectedMedia}
                                onChange={(e) => setSelectedMedia(e.target.value)}
                                className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                                <option value="전체">전체 매체</option>
                                <option value="블로그">블로그</option>
                                <option value="인스타그램">인스타그램</option>
                                <option value="릴스/숏츠">릴스/숏츠</option>
                                <option value="유튜브">유튜브</option>
                            </select>
                        </div>

                        {/* 정렬 옵션 */}
                        <div className="flex items-center space-x-2 text-xs">
                            <span className="text-slate-400">정렬:</span>
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-700 focus:outline-none"
                            >
                                <option value="end_date_asc">마감 임박순</option>
                                <option value="created_desc">최신 등록순</option>
                                <option value="applied_desc">신청자 많은순</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* 3. 검색 결과 요약 헤더 */}
                <div className="flex items-center justify-between px-1">
                    <p className="text-sm text-slate-600">
                        총 <span className="font-bold text-indigo-600">{filteredCampaigns.length}</span>개의 체험단 공고가 있습니다.
                    </p>
                    {(selectedPlatform !== "전체" || selectedCategory !== "all" || selectedLocation !== "전체 지역" || searchTerm) && (
                        <button
                            onClick={() => {
                                setSelectedPlatform("전체");
                                setSelectedCategory("all");
                                setSelectedLocation("전체 지역");
                                setSelectedMedia("전체");
                                setSearchTerm("");
                                setShowOnlyBookmarks(false);
                            }}
                            className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center space-x-1"
                        >
                            <i className="fa-solid fa-rotate-right"></i>
                            <span>필터 초기화</span>
                        </button>
                    )}
                </div>

                {/* 4. 캠페인 카드 그리드 목록 */}
                {loading ? (
                    <div className="py-24 text-center">
                        <i className="fa-solid fa-spinner fa-spin text-4xl text-indigo-600"></i>
                        <p className="mt-4 text-sm text-slate-500 font-medium">체험단 공고를 불러오는 중입니다...</p>
                    </div>
                ) : filteredCampaigns.length === 0 ? (
                    <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 max-w-md mx-auto my-8 space-y-3">
                        <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto text-2xl">
                            <i className="fa-regular fa-folder-open"></i>
                        </div>
                        <h3 className="text-base font-bold text-slate-800">조건에 맞는 체험단이 없습니다</h3>
                        <p className="text-xs text-slate-500">다른 검색어를 입력하거나 필터 조건을 변경해보세요.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                        {filteredCampaigns.map(c => {
                            const dday = getDDay(c.end_date);
                            const platformBadge = getPlatformBadge(c.platform);
                            const isBookmarked = bookmarks.includes(c.id);

                            return (
                                <div
                                    key={c.id}
                                    className="campaign-card bg-white rounded-2xl border border-slate-200 overflow-hidden flex flex-col justify-between group"
                                >
                                    {/* 상단 썸네일 이미지 및 뱃지 */}
                                    <div className="relative card-image-wrap aspect-[4/3] bg-slate-100 overflow-hidden">
                                        <img
                                            src={c.image_url || "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=600&auto=format&fit=crop&q=80"}
                                            alt={c.title}
                                            className="w-full h-full object-cover"
                                            onError={(e) => {
                                                e.target.src = "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=600&auto=format&fit=crop&q=80";
                                            }}
                                        />

                                        {/* D-Day 뱃지 */}
                                        <div className="absolute top-3 left-3">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-bold shadow-sm ${
                                                dday.isUrgent
                                                    ? "bg-rose-500 text-white badge-urgent"
                                                    : "bg-slate-900/80 backdrop-blur-md text-white"
                                            }`}>
                                                {dday.text}
                                            </span>
                                        </div>

                                        {/* 찜하기(하트) 버튼 */}
                                        <button
                                            onClick={(e) => toggleBookmark(c.id, e)}
                                            className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur-md text-rose-500 flex items-center justify-center shadow-md hover:scale-110 transition-transform"
                                            title="관심 체험단 찜하기"
                                        >
                                            <i className={`${isBookmarked ? "fa-solid text-rose-500" : "fa-regular text-slate-400"} text-sm`}></i>
                                        </button>

                                        {/* 미디어 유형 뱃지 (블로그, 인스타 등) */}
                                        <div className="absolute bottom-3 left-3">
                                            <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold ${getMediaBadge(c.media_type)}`}>
                                                {c.media_type || "블로그"}
                                            </span>
                                        </div>
                                    </div>

                                    {/* 카드 본문 내용 */}
                                    <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                                        <div className="space-y-1.5">
                                            {/* 플랫폼 & 지역 */}
                                            <div className="flex items-center justify-between text-xs">
                                                <span className={`px-2 py-0.5 rounded border text-[11px] font-bold ${platformBadge.bg}`}>
                                                    <i className={`fa-solid ${platformBadge.icon} mr-1`}></i>
                                                    {c.platform}
                                                </span>
                                                <span className="text-slate-500 font-medium truncate max-w-[120px]">
                                                    <i className="fa-solid fa-location-dot text-slate-400 mr-1"></i>
                                                    {c.location || "전국"}
                                                </span>
                                            </div>

                                            {/* 캠페인 제목 */}
                                            <h2 className="font-bold text-slate-900 text-sm sm:text-base line-clamp-2 group-hover:text-indigo-600 transition-colors leading-snug">
                                                {c.title}
                                            </h2>

                                            {/* 제공 혜택 */}
                                            {c.reward && (
                                                <p className="text-xs text-indigo-700 bg-indigo-50/70 rounded-lg p-2 font-medium line-clamp-2 border border-indigo-100/50">
                                                    <i className="fa-solid fa-gift mr-1 text-indigo-500"></i>
                                                    {c.reward}
                                                </p>
                                            )}
                                        </div>

                                        {/* 모집 인원 및 신청 인원 프로그레스 */}
                                        <div className="space-y-3 pt-2 border-t border-slate-100">
                                            <div className="flex items-center justify-between text-xs text-slate-500">
                                                <span>신청 <strong className="text-slate-800">{c.applied_count || 0}</strong>명</span>
                                                <span>모집 <strong className="text-indigo-600">{c.capacity || 10}</strong>명</span>
                                            </div>

                                            {/* 원문 신청 페이지 이동 버튼 (아웃링크) */}
                                            <a
                                                href={c.original_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-indigo-600 text-white font-semibold text-xs text-center flex items-center justify-center space-x-1.5 transition-colors shadow-sm"
                                            >
                                                <span>신청하러 가기</span>
                                                <i className="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </main>

            {/* 하단 푸터 */}
            <footer className="bg-slate-900 text-slate-400 text-xs py-8 border-t border-slate-800 mt-12">
                <div className="max-w-7xl mx-auto px-4 text-center space-y-2">
                    <p className="font-semibold text-slate-300">Experience Hub · 국내 체험단 통합 검색 플랫폼</p>
                    <p>본 사이트는 각 플랫폼의 공개 모집 공고를 아웃링크 형태로 제공하며, 모든 캠페인의 저작권 및 운영 권한은 해당 플랫폼에 있습니다.</p>
                </div>
            </footer>
        </div>
    );
}

// React 루트 렌더링
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
