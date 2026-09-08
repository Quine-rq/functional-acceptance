"""Run once in this isolated clone. Refuse an existing database or credentials."""
import json
import os
from pathlib import Path
import secrets
import sys

root = Path(__file__).resolve().parent
if (root / "db.sqlite3").exists() or (root / "private.json").exists():
    raise SystemExit("Refusing to replace existing study state")
for name in ("assets", "favicons", "previews", "article", "artifacts"):
    (root / name).mkdir(exist_ok=True)
private = {"django_secret": secrets.token_urlsafe(40), "users": {
    name: secrets.token_urlsafe(24) for name in ("fa_alice", "fa_bob")}}
with (root / "private.json").open("x") as f:
    os.chmod(f.name, 0o600)
    json.dump(private, f)
sys.path.insert(0, str(root.parent))
os.environ["DJANGO_SETTINGS_MODULE"] = "study_settings"
os.environ["LD_DISABLE_BACKGROUND_TASKS"] = "True"
import django
django.setup()
from django.core.management import call_command
from django.contrib.auth.models import User
call_command("migrate", interactive=False, verbosity=0)
for name, password in private["users"].items():
    user = User.objects.create_user(username=name, password=password)
    profile = user.profile
    profile.enable_sharing = False
    profile.enable_public_sharing = False
    profile.enable_favicons = False
    profile.enable_preview_images = False
    profile.enable_automatic_html_snapshots = False
    profile.save()
print("Prepared isolated database with two ordinary synthetic users; secrets not printed.")
