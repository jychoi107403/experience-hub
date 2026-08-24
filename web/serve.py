# ==============================================================================
# 파일명: web/serve.py
# 설명: 초보자도 명령어 한 줄로 웹 사이트를 즉시 띄우고 브라우저로 확인할 수 있는 로컬 웹 서버
# 실행 방법: python web/serve.py
# ==============================================================================

import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Windows 콘솔 인코딩 대응
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 3000


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # web 폴더를 웹 루트로 서빙
        directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=directory, **kwargs)


def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, CustomHandler)
    url = f"http://localhost:{PORT}"

    print("=" * 60)
    print(" 🎁 Experience Hub 웹 서비스가 성공적으로 시작되었습니다! 🎁 ")
    print("=" * 60)
    print(f"👉 브라우저 주소: {url}")
    print("💡 서버를 종료하려면 터미널에서 Ctrl + C를 누르세요.")
    print("=" * 60)

    # 브라우저 자동 오픈
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n웹 서버를 안전하게 종료했습니다.")


if __name__ == "__main__":
    run_server()
