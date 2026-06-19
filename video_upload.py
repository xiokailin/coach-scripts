#!/usr/bin/env python3
"""Upload student training videos from ~/Downloads to Google Drive.

Usage:
  python3 video_upload.py 黃蕙敏            # 只上傳 Drive（備份）
  python3 video_upload.py 黃蕙敏 --line     # 上傳 Drive + 輸出 LINE-ready JSON
  python3 video_upload.py 黃蕙敏 --date 6/9 # 指定 Drive 日期子資料夾名稱

Output (--line flag):
  JSON to stdout, format:
  {"videos": [{"name": "IMG_xxx.MOV", "mp4_id": "...", "thumb_id": "...",
               "mp4_url": "...", "thumb_url": "..."}],
   "folder_url": "https://drive.google.com/..."}
"""

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List

DOWNLOADS = Path.home() / "Downloads"
LOG_FILE = Path.home() / ".claude" / "video_upload_log.txt"
CACHE_FILE = Path.home() / ".claude" / "student_folders.json"
GWS = "/opt/homebrew/bin/gws"
WINDOW_HOURS = 2
VIDEO_EXTS = {".mov", ".mp4"}
IMAGE_EXTS = {".heic", ".jpg", ".jpeg", ".png"}
ALL_EXTS = VIDEO_EXTS | IMAGE_EXTS
IMAGE_MIME = {".heic": "image/heic", ".jpg": "image/jpeg",
              ".jpeg": "image/jpeg", ".png": "image/png"}


def get_ctime(filepath: Path) -> datetime:
    return datetime.fromtimestamp(os.stat(filepath).st_ctime, tz=timezone.utc)


def read_uploaded() -> set:
    """Return the set of filenames already recorded in the upload log."""
    if LOG_FILE.exists():
        return set(LOG_FILE.read_text().strip().splitlines())
    return set()


def find_new_files() -> List[Path]:
    """Find files with ctime within last WINDOW_HOURS, not already logged."""
    uploaded = read_uploaded()

    now = datetime.now(tz=timezone.utc)
    cutoff = now - timedelta(hours=WINDOW_HOURS)

    results = []
    for f in DOWNLOADS.iterdir():
        if f.suffix.lower() not in ALL_EXTS:
            continue
        if f.name in uploaded:
            continue
        ct = get_ctime(f)
        if ct >= cutoff:
            results.append((ct, f))

    return [f for _, f in sorted(results)]


def convert_to_mp4(src: Path) -> Path:
    """Convert MOV to MP4 (H.264/AAC). Returns path to .mp4 file."""
    out = src.with_suffix(".mp4")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src),
         "-c:v", "libx264", "-c:a", "aac", "-movflags", "faststart",
         str(out)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 轉換失敗：{result.stderr[-300:]}")
    return out


def extract_thumbnail(video: Path) -> Path:
    """Extract frame at 1s as JPEG thumbnail. Returns path to .jpg file."""
    out = video.with_suffix(".thumb.jpg")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(video),
         "-ss", "00:00:01", "-vframes", "1", str(out)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"縮圖擷取失敗：{result.stderr[-200:]}")
    return out


def load_folder_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_folder_cache(cache: dict):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))


def search_drive_folder(student_name: str) -> Optional[str]:
    print(f"搜尋 Drive 中 {student_name} 的資料夾...", file=sys.stderr)
    result = subprocess.run(
        [GWS, "drive", "files", "list", "--params", json.dumps({
            "q": f"name='{student_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            "fields": "files(id,name)"
        })],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"搜尋失敗：{result.stderr}", file=sys.stderr)
        return None
    files = json.loads(result.stdout).get("files", [])
    if not files:
        return None
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


def get_or_create_subfolder(name: str, parent_id: str) -> str:
    result = subprocess.run(
        [GWS, "drive", "files", "list", "--params", json.dumps({
            "q": f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            "fields": "files(id)"
        })],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        files = json.loads(result.stdout).get("files", [])
        if files:
            return files[0]["id"]

    result = subprocess.run(
        [GWS, "drive", "files", "create",
         "--json", json.dumps({
             "name": name,
             "mimeType": "application/vnd.google-apps.folder",
             "parents": [parent_id]
         })],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"建立資料夾失敗：{result.stderr}")
    return json.loads(result.stdout)["id"]


def upload_file(filepath: Path, folder_id: str, mime: str) -> str:
    """Upload file to Drive folder. Returns file ID."""
    result = subprocess.run(
        [GWS, "drive", "files", "create",
         "--json", json.dumps({"name": filepath.name, "parents": [folder_id]}),
         "--upload", filepath.name,
         "--upload-content-type", mime],
        capture_output=True, text=True,
        cwd=str(filepath.parent)
    )
    if result.returncode != 0:
        raise RuntimeError(f"上傳失敗：{result.stderr}")
    return json.loads(result.stdout)["id"]


def set_public(file_id: str):
    """Set Drive file readable by anyone with link."""
    result = subprocess.run(
        [GWS, "drive", "permissions", "create",
         "--params", json.dumps({"fileId": file_id}),
         "--json", json.dumps({"role": "reader", "type": "anyone"})],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"設定公開失敗：{result.stderr}")


def drive_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?id={file_id}&export=download"


def log_uploaded(filename: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(filename + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("student_name")
    parser.add_argument("--line", action="store_true", help="輸出 LINE-ready JSON")
    parser.add_argument("--date", default=None, help="Drive 日期子資料夾名稱，格式 M/D，預設今天")
    parser.add_argument("--folder-id", default=None)
    args = parser.parse_args()

    today = datetime.now()
    date_str = args.date or f"{today.month}/{today.day}"

    # Find new files
    files = find_new_files()
    if not files:
        uploaded = read_uploaded()
        already = [f.name for f in DOWNLOADS.iterdir() if f.suffix.lower() in ALL_EXTS and f.name in uploaded]
        if already:
            print(f"找不到新檔案。Downloads 有 {len(already)} 個已上傳的同名檔案（可能重複上傳）。", file=sys.stderr)
        else:
            print(f"找不到 {WINDOW_HOURS} 小時內的新檔案（已排除已上傳檔案）", file=sys.stderr)
        sys.exit(0)

    print(f"找到 {len(files)} 個檔案：", file=sys.stderr)
    for f in files:
        print(f"  {f.name} ({f.stat().st_size/1e6:.1f} MB)", file=sys.stderr)

    # Get student folder
    folder_id = args.folder_id or get_student_folder_id(args.student_name)
    if not folder_id:
        print(f"找不到 {args.student_name} 的 Drive 資料夾，請提供 --folder-id", file=sys.stderr)
        sys.exit(1)

    # Get or create date subfolder
    print(f"取得或建立資料夾 {date_str}...", file=sys.stderr)
    subfolder_id = get_or_create_subfolder(date_str, folder_id)
    folder_url = f"https://drive.google.com/drive/folders/{subfolder_id}"

    results = []
    for src in files:
        original_name = src.name
        thumb_path = None
        try:
            # MOV needs conversion to MP4; everything else uploads as-is
            upload_path = src
            if src.suffix.lower() == ".mov":
                print(f"轉換 {src.name} → MP4...", file=sys.stderr)
                upload_path = convert_to_mp4(src)

            is_video = src.suffix.lower() in VIDEO_EXTS
            mime = "video/mp4" if is_video else IMAGE_MIME.get(src.suffix.lower(), "image/jpeg")

            # Extract thumbnail for videos
            if is_video:
                print(f"擷取縮圖...", file=sys.stderr)
                thumb_path = extract_thumbnail(upload_path)

            # Upload main file
            print(f"上傳 {upload_path.name}...", file=sys.stderr)
            file_id = upload_file(upload_path, subfolder_id, mime)

            if args.line:
                set_public(file_id)

            # Upload thumbnail
            thumb_id = None
            if thumb_path:
                print(f"上傳縮圖...", file=sys.stderr)
                thumb_id = upload_file(thumb_path, subfolder_id, "image/jpeg")
                if args.line:
                    set_public(thumb_id)

            # Delete local files (src plus any converted mp4 / thumbnail)
            for p in {src, upload_path, thumb_path}:
                if p:
                    p.unlink(missing_ok=True)

            log_uploaded(original_name)
            print(f"  完成", file=sys.stderr)

            results.append({
                "name": original_name,
                "mp4_id": file_id,
                "thumb_id": thumb_id,
                "mp4_url": drive_url(file_id),
                "thumb_url": drive_url(thumb_id) if thumb_id else None,
            })

        except RuntimeError as e:
            print(f"  失敗：{e}", file=sys.stderr)

    print(f"\n完成：{len(results)} 成功", file=sys.stderr)

    if args.line:
        # Output JSON to stdout for Claude to read and handle LINE send
        print(json.dumps({"videos": results, "folder_url": folder_url}, ensure_ascii=False))
    else:
        print(f"Drive 資料夾：{folder_url}", file=sys.stderr)


if __name__ == "__main__":
    main()
