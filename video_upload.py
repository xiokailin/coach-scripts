#!/usr/bin/env python3
"""Upload student training videos from ~/Downloads to Google Drive."""

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List, Tuple

DOWNLOADS = Path.home() / "Downloads"
LOG_FILE = Path.home() / ".claude" / "video_upload_log.txt"
CACHE_FILE = Path.home() / ".claude" / "student_folders.json"
WINDOW_HOURS = 2
VIDEO_EXTS = {".mov", ".mp4", ".MOV", ".MP4", ".heic", ".HEIC", ".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG"}


def get_ctime(filepath: Path) -> datetime:
    # ctime = inode change time; set when file is written to this Mac (e.g., via AirDrop)
    # Unlike mtime/btime, ctime is NOT preserved from the source device
    return datetime.fromtimestamp(os.stat(filepath).st_ctime, tz=timezone.utc)


def find_new_videos(date_str: Optional[str] = None) -> List[Path]:
    """Find unlogged videos whose ctime falls within the target window.

    - No date_str (today): ctime within last WINDOW_HOURS hours
    - Past date_str (e.g. '5/19'): ctime within that calendar day (local time) + 6h buffer into next day
    """
    uploaded = set()
    if LOG_FILE.exists():
        uploaded = set(LOG_FILE.read_text().strip().splitlines())

    now = datetime.now(tz=timezone.utc)
    if date_str is None:
        cutoff_start = now - timedelta(hours=WINDOW_HOURS)
        cutoff_end = now
    else:
        month, day = map(int, date_str.split("/"))
        year = now.year
        local_tz = datetime.now().astimezone().tzinfo
        day_start = datetime(year, month, day, 0, 0, 0, tzinfo=local_tz)
        cutoff_start = day_start
        cutoff_end = day_start + timedelta(hours=30)  # covers class day + next morning

    results = []
    for f in DOWNLOADS.iterdir():
        if f.suffix not in VIDEO_EXTS:
            continue
        if f.name in uploaded:
            continue
        ctime = get_ctime(f)
        if cutoff_start <= ctime <= cutoff_end:
            results.append((ctime, f))

    return [f for _, f in sorted(results)]


def load_folder_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_folder_cache(cache: dict):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))


def search_drive_folder(student_name: str) -> Optional[str]:
    print(f"搜尋 Drive 中 {student_name} 的資料夾...")
    result = subprocess.run(
        ["gws", "drive", "files", "list", "--params", json.dumps({
            "q": f"name contains '{student_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
            "fields": "files(id,name)"
        })],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"搜尋失敗：{result.stderr}")
        return None
    data = json.loads(result.stdout)
    files = data.get("files", [])
    if not files:
        return None
    # Prefer exact name match
    for f in files:
        if f["name"] == student_name:
            return f["id"]
    return files[0]["id"]


def get_student_folder_id(student_name: str) -> Optional[str]:
    cache = load_folder_cache()
    if student_name in cache:
        return cache[student_name]
    folder_id = search_drive_folder(student_name)
    if folder_id:
        cache[student_name] = folder_id
        save_folder_cache(cache)
    return folder_id


def get_or_create_drive_folder(name: str, parent_id: str) -> dict:
    # Check if folder already exists
    result = subprocess.run(
        ["gws", "drive", "files", "list", "--params", json.dumps({
            "q": f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
            "fields": "files(id,name,webViewLink)"
        })],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        files = json.loads(result.stdout).get("files", [])
        if files:
            f = files[0]
            f.setdefault("webViewLink", f"https://drive.google.com/drive/folders/{f['id']}")
            return f

    # Create new folder
    result = subprocess.run(
        ["gws", "drive", "files", "create",
         "--params", json.dumps({"fields": "id,name,webViewLink"}),
         "--json", json.dumps({
             "name": name,
             "mimeType": "application/vnd.google-apps.folder",
             "parents": [parent_id]
         })],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"建立資料夾失敗：{result.stderr}")
    return json.loads(result.stdout)


def upload_video(filepath: Path, folder_id: str) -> dict:
    ext = filepath.suffix.lower()
    mime = {
        ".mov": "video/quicktime",
        ".mp4": "video/mp4",
        ".heic": "image/heic",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }.get(ext, "application/octet-stream")
    # gws only allows files within cwd; run from the file's parent directory
    result = subprocess.run(
        ["gws", "drive", "files", "create",
         "--params", json.dumps({"fields": "id,name"}),
         "--json", json.dumps({
             "name": filepath.name,
             "parents": [folder_id]
         }),
         "--upload", filepath.name,
         "--upload-content-type", mime],
        capture_output=True, text=True,
        cwd=str(filepath.parent)
    )
    if result.returncode != 0:
        raise RuntimeError(f"上傳失敗：{result.stderr}")
    return json.loads(result.stdout)


def log_uploaded(filename: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(filename + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("student_name")
    parser.add_argument("--date", default=None, help="上課日期，格式 M/D，預設今天")
    parser.add_argument("--folder-id", default=None)
    args = parser.parse_args()

    student_name = args.student_name
    folder_id_override = args.folder_id

    # date_str controls only the Drive folder name; search always uses 2-hour ctime window
    if args.date:
        date_str = args.date
    else:
        today = datetime.now()
        date_str = f"{today.month}/{today.day}"

    # Find videos (always 2-hour ctime window); --date only controls Drive folder name
    videos = find_new_videos(date_str=None)
    if not videos:
        # Check if any videos in Downloads are already in the log
        uploaded = set()
        if LOG_FILE.exists():
            uploaded = set(LOG_FILE.read_text().strip().splitlines())
        already = [f.name for f in DOWNLOADS.iterdir() if f.suffix in VIDEO_EXTS and f.name in uploaded]
        if already:
            print(f"找不到新影片。注意：Downloads 有 {len(already)} 支已上傳過的同名影片，可能是重複上傳。")
        else:
            print(f"找不到 {WINDOW_HOURS} 小時內的新影片（已排除已上傳檔案）")
        sys.exit(0)

    print(f"找到 {len(videos)} 支影片：")
    for v in videos:
        size_mb = v.stat().st_size / 1_000_000
        print(f"  {v.name} ({size_mb:.1f} MB)")

    # Get student folder
    folder_id = folder_id_override or get_student_folder_id(student_name)
    if not folder_id:
        print(f"找不到 {student_name} 的 Drive 資料夾，請提供 --folder-id")
        sys.exit(1)

    # Get or create date subfolder
    print(f"取得或建立資料夾 {date_str}...")
    subfolder = get_or_create_drive_folder(date_str, folder_id)
    subfolder_id = subfolder["id"]
    subfolder_link = subfolder.get("webViewLink", f"https://drive.google.com/drive/folders/{subfolder_id}")

    # Upload and delete
    success, failed = [], []
    for video in videos:
        size_mb = video.stat().st_size / 1_000_000
        print(f"上傳 {video.name} ({size_mb:.1f} MB)...")
        try:
            upload_video(video, subfolder_id)
            log_uploaded(video.name)
            video.unlink()
            success.append(video.name)
            print(f"  完成並刪除本地檔案")
        except RuntimeError as e:
            failed.append(video.name)
            print(f"  失敗：{e}")

    print(f"\n完成：{len(success)} 成功 / {len(failed)} 失敗")
    if subfolder_link:
        print(f"Drive 資料夾：{subfolder_link}")
    if failed:
        print(f"上傳失敗（本地保留）：{', '.join(failed)}")


if __name__ == "__main__":
    main()
