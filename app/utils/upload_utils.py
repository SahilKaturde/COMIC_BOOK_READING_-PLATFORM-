# app/utils/upload_utils.py

import os
import shutil

# --- SAFETY SHIELD ---
# The Cloudinary SDK crashes on import if CLOUDINARY_URL exists but is invalid.
# We MUST sanitize the environment BEFORE importing it.
cl_url = os.environ.get("CLOUDINARY_URL")
if cl_url and not cl_url.startswith("cloudinary://"):
    os.environ.pop("CLOUDINARY_URL")

import cloudinary
import cloudinary.uploader

# Project root → Data/ folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_ROOT = os.path.join(PROJECT_ROOT, "Data")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "jfif"}

# Cloudinary Configuration (Using separate variables to avoid auto-config errors)
CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
API_KEY = os.environ.get("CLOUDINARY_API_KEY")
API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

if CLOUD_NAME and API_KEY and API_SECRET:
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET,
        secure=True
    )
    IS_CLOUDINARY = True
else:
    # Also support the single URL if provided correctly
    CL_URL = os.environ.get("CLOUDINARY_URL")
    if CL_URL and CL_URL.startswith("cloudinary://"):
        cloudinary.config(cloudinary_url=CL_URL)
        IS_CLOUDINARY = True
    else:
        IS_CLOUDINARY = False


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    """Extract the file extension."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else "png"


def save_upload(file_obj, *path_parts):
    """
    Save an uploaded file to Cloudinary (if configured) or local Data/ folder.

    Args:
        file_obj: werkzeug FileStorage object
        *path_parts: path segments, e.g. ("comics", "5", "poster.jpg")

    Returns:
        Full URL (if Cloudinary) or relative path (if local).
    """
    if IS_CLOUDINARY:
        # Construct a folder/public_id from path_parts
        # e.g., "comics/5/poster"
        public_id = "/".join(path_parts).rsplit(".", 1)[0]
        upload_result = cloudinary.uploader.upload(
            file_obj,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        return upload_result["secure_url"]

    # Local Fallback
    relative_path = os.path.join(*path_parts)
    absolute_path = os.path.join(DATA_ROOT, relative_path)

    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    file_obj.save(absolute_path)
    return relative_path.replace("\\", "/")


def save_poster(file_obj, comic_id):
    """Save a comic poster image."""
    ext = get_extension(file_obj.filename)
    return save_upload(file_obj, "comics", str(comic_id), f"poster.{ext}")


def save_publisher_logo(file_obj, publisher_id):
    """Save a publisher logo image."""
    ext = get_extension(file_obj.filename)
    return save_upload(file_obj, "publishers", str(publisher_id), f"logo.{ext}")


def save_page_image(file_obj, comic_id, chapter_number, page_number):
    """Save a comic page image."""
    ext = get_extension(file_obj.filename)
    return save_upload(
        file_obj,
        "comics", str(comic_id), "chapters", str(chapter_number), f"{page_number}.{ext}"
    )


def delete_folder(*path_parts):
    """Delete a folder inside Data/. (Note: Cloudinary folder deletion not implemented yet)"""
    folder_path = os.path.join(DATA_ROOT, *[str(p) for p in path_parts])
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


def delete_file(*path_parts):
    """Delete a single file inside Data/ or from Cloudinary."""
    if IS_CLOUDINARY:
        public_id = "/".join([str(p) for p in path_parts]).rsplit(".", 1)[0]
        cloudinary.uploader.destroy(public_id)
        return

    file_path = os.path.join(DATA_ROOT, *[str(p) for p in path_parts])
    if os.path.exists(file_path):
        os.remove(file_path)
