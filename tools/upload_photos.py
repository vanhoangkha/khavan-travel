"""Upload photos to Cloudflare R2 for travel landing page.

Usage:
  1. Export photos from Google Takeout or iCloud into a folder
  2. pip install boto3 pillow
  3. python upload_photos.py /path/to/photos

Photos are resized to max 1600px width and converted to JPEG for web performance.
Outputs a JSON file (photos.json) with all public URLs for the landing page.
"""
import sys, os, json, hashlib
from pathlib import Path

try:
    import boto3
    from PIL import Image
except ImportError:
    print("Run: pip install boto3 pillow")
    sys.exit(1)

# --- Config from .env or environment ---
ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "599cbc5a10bed4b414e4cfba6ccce6d4")
BUCKET = os.getenv("R2_BUCKET", "kha-travel-photos")
# R2 uses S3-compatible API — needs Access Key ID & Secret (create in CF dashboard > R2 > Manage API tokens)
ACCESS_KEY = os.getenv("R2_ACCESS_KEY", "")
SECRET_KEY = os.getenv("R2_SECRET_KEY", "")
PUBLIC_URL = os.getenv("R2_PUBLIC_URL", f"https://photos.cloudsecop.net")

MAX_WIDTH = 1600
THUMB_WIDTH = 400
QUALITY = 82

def resize(img_path, max_w):
    img = Image.open(img_path)
    img = img.convert("RGB")
    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
    return img

def upload(s3, local_path, key):
    s3.upload_file(str(local_path), BUCKET, key,
                   ExtraArgs={"ContentType": "image/jpeg", "CacheControl": "public, max-age=31536000"})
    return f"{PUBLIC_URL}/{key}"

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} /path/to/photos")
        sys.exit(1)

    photo_dir = Path(sys.argv[1])
    if not photo_dir.is_dir():
        print(f"Not a directory: {photo_dir}")
        sys.exit(1)

    if not ACCESS_KEY or not SECRET_KEY:
        print("Set R2_ACCESS_KEY and R2_SECRET_KEY environment variables.")
        print("Create them at: Cloudflare Dashboard > R2 > Manage R2 API Tokens")
        sys.exit(1)

    s3 = boto3.client("s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name="auto")

    # Ensure bucket exists
    try:
        s3.head_bucket(Bucket=BUCKET)
    except Exception:
        s3.create_bucket(Bucket=BUCKET)
        print(f"Created bucket: {BUCKET}")

    exts = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
    files = sorted(f for f in photo_dir.rglob("*") if f.suffix.lower() in exts)
    print(f"Found {len(files)} photos")

    results = []
    tmp_dir = Path("/tmp/kha-travel-resize")
    tmp_dir.mkdir(exist_ok=True)

    for i, f in enumerate(files, 1):
        name = hashlib.md5(str(f).encode()).hexdigest()[:12]
        print(f"[{i}/{len(files)}] {f.name}")

        # Full size
        full = resize(f, MAX_WIDTH)
        full_path = tmp_dir / f"{name}.jpg"
        full.save(full_path, "JPEG", quality=QUALITY)
        full_url = upload(s3, full_path, f"full/{name}.jpg")

        # Thumbnail
        thumb = resize(f, THUMB_WIDTH)
        thumb_path = tmp_dir / f"{name}_thumb.jpg"
        thumb.save(thumb_path, "JPEG", quality=75)
        thumb_url = upload(s3, thumb_path, f"thumb/{name}.jpg")

        results.append({"src": full_url, "thumb": thumb_url, "original": f.name})

    out = Path("photos.json")
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nDone! {len(results)} photos uploaded. URLs saved to {out}")

if __name__ == "__main__":
    main()
