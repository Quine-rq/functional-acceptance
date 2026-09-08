"""Study-only environment; upstream application code remains unchanged."""
import json
from pathlib import Path

from bookmarks.settings.dev import *  # noqa: F403

STUDY_ROOT = Path(__file__).resolve().parent
SECRET_KEY = json.loads((STUDY_ROOT / "private.json").read_text())["django_secret"]
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
DATABASES["default"]["NAME"] = str(STUDY_ROOT / "db.sqlite3")
HUEY["filename"] = str(STUDY_ROOT / "tasks.sqlite3")
LD_DISABLE_BACKGROUND_TASKS = True
LD_DISABLE_URL_VALIDATION = False
LD_ENABLE_SNAPSHOTS = False
LD_ENABLE_REFRESH_FAVICONS = False
LD_ASSET_FOLDER = str(STUDY_ROOT / "assets")
LD_FAVICON_FOLDER = str(STUDY_ROOT / "favicons")
LD_PREVIEW_FOLDER = str(STUDY_ROOT / "previews")
LD_FAVICON_PROVIDER = "http://127.0.0.1:18742/favicon/{url}"
STATICFILES_DIRS = [str(Path(BASE_DIR) / "bookmarks" / "styles"), LD_FAVICON_FOLDER, LD_PREVIEW_FOLDER]
