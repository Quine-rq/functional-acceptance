"""Prepare a fresh isolated study; never install dependencies or replace state."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import sys
from support import validate_project, publish_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    root = validate_project(args.project)
    state = root / ".acceptance-study"
    state.mkdir(mode=0o700)  # Exclusive ownership; refuses partial prior preparation.
    status = {"state": "incomplete", "owned_directory": str(state)}
    try:
        for name in ("assets", "favicons", "previews", "article", "artifacts"):
            (state / name).mkdir(mode=0o700)
        template = Path(__file__).parent / "environment"
        shutil.copyfile(template / "study_settings.py", state / "study_settings.py")
        shutil.copyfile(template / "article.html", state / "article" / "article.html")
        private = {"django_secret": secrets.token_urlsafe(40), "users": {
            name: secrets.token_urlsafe(24) for name in ("fa_alice", "fa_bob")}}
        fd = os.open(state / "private.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(private, stream)
        sys.path[:0] = [str(state), str(root)]
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
            for flag in ("enable_sharing", "enable_public_sharing", "enable_favicons",
                         "enable_preview_images", "enable_automatic_html_snapshots"):
                setattr(profile, flag, False)
            profile.save()
        status["state"] = "prepared"
    except Exception as error:
        status["error_type"] = type(error).__name__
        status["next"] = "Keep this owned partial state; inspect locally, then prepare a new isolated checkout. No automatic deletion."
    publish_json(state / "preparation.json", status)
    print(json.dumps(status))
    return 0 if status["state"] == "prepared" else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(json.dumps({"state": "unprepared", "error_type": type(error).__name__,
                          "next": "Check pinned source and a fresh destination; no state was replaced."}))
        sys.exit(2)
