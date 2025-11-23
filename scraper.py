import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
from db import IC_DB

class Cast_Scraper:
    def __init__(self, db_path="db/IC_data.db"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        })
        self.db = IC_DB(db_path)

    def _get_soup(self, url):
        try:
            res = self.session.get(url, timeout=10)
            res.raise_for_status()
            return BeautifulSoup(res.content, "html.parser")
        except requests.RequestException as e:
            print(f"[ERROR] 無法連線到 {url}：{e}")
            return None

    def _safe_text(self, tag):
        return tag.get_text(strip=True) if tag else ""

    def _sanitize_folder_name(self, name):
        if not name:
            return "unknown"
        cleaned = []
        for c in name:
            if c.isspace():
                cleaned.append("_")
            elif c.isalnum() or c in ("_", "-"):
                cleaned.append(c)
        folder_name = "".join(cleaned).strip("_")
        return folder_name or "unknown"

    def scrape_all(self, base_url="https://imaginary-base.jp", limit=None):
        cast_list_url = urljoin(base_url, "/cast/")
        cast_list_page = self._get_soup(cast_list_url)
        if not cast_list_page:
            yield "無法取得演員列表頁面"
            return

        items = cast_list_page.select("div.thumb.js-modal_open.js-dynamic_open") or cast_list_page.select("div.thumb")
        total = len(items)
        yield f"共找到 {total} 位演員"

        for i, item in enumerate(items):
            if limit and i >= limit:
                break

            cast_id = item.get("data-permalink") or item.get("data-permalink-url") or item.get("data-url")
            if not cast_id:
                yield f"[{i+1}/{total}] 找不到演員連結，跳過"
                continue

            detail_url = urljoin(base_url, cast_id)
            detail_soup = self._get_soup(detail_url)
            if not detail_soup:
                yield f"[{i+1}/{total}] 無法讀取 {detail_url}"
                continue

            try:
                jp_name = self._safe_text(detail_soup.find("h4", class_="name_jp"))
                en_name = self._safe_text(detail_soup.find("span", class_="c-ahfix"))
                caption = self._safe_text(detail_soup.find("div", class_="caption"))

                img_tag = (detail_soup.find("div", class_="cast_single__mainph") or detail_soup).find("img")
                if not img_tag or not img_tag.get("src"):
                    yield f"[{i+1}/{total}] 無法找到圖片，跳過"
                    continue

                img_url = urljoin(base_url, img_tag.get("src"))

                save_dir = os.path.join("IC_images", self._sanitize_folder_name(jp_name or en_name or cast_id))
                os.makedirs(save_dir, exist_ok=True)

                parsed = urlparse(img_tag.get("src"))
                img_filename = os.path.basename(parsed.path) or f"image_{int(time.time())}.png"
                img_path = os.path.join(save_dir, img_filename)

                try:
                    r = self.session.get(img_url, timeout=15)
                    r.raise_for_status()
                    with open(img_path, "wb") as f:
                        f.write(r.content)
                except requests.RequestException as e:
                    yield f"[{i+1}/{total}] 下載圖片失敗：{img_url}  錯誤：{e}"
                    continue

                db_img_path = os.path.normpath(img_path).replace("\\", "/")
                self.db.save_cast(cast_id, jp_name, en_name, caption, db_img_path)

                yield f"[{i+1}/{total}] 已更新：{jp_name} ({en_name})"
                time.sleep(0.5)

            except Exception as e:
                yield f"[{i+1}/{total}] 錯誤：{e}"

        yield f"✅ 完成：共 {total} 筆資料已更新"

if __name__ == "__main__":
    scraper = Cast_Scraper()
    for msg in scraper.scrape_all(limit=5):
        print(msg)
