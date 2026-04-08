# app/utils/upload_utils.py

import os
import shutil

# Project root → Data/ folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_ROOT = os.path.join(PROJECT_ROOT, "Data")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "jfif"}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    """Extract the file extension."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else "png"


def save_upload(file_obj, *path_parts):
    """
    Save an uploaded file to Data/<path_parts>.

    Args:
        file_obj: werkzeug FileStorage object
        *path_parts: path segments, e.g. ("comics", "5", "poster.jpg")

    Returns:
        Relative path from Data root, e.g. "comics/5/poster.jpg"
    """
    relative_path = os.path.join(*path_parts)
    absolute_path = os.path.join(DATA_ROOT, relative_path)

    # Ensure directory exists
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

    # Save
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
    """Delete a folder inside Data/. Used for cascade cleanup."""
    folder_path = os.path.join(DATA_ROOT, *[str(p) for p in path_parts])
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


def delete_file(*path_parts):
    """Delete a single file inside Data/."""
    file_path = os.path.join(DATA_ROOT, *[str(p) for p in path_parts])
    if os.path.exists(file_path):
        os.remove(file_path)
