"""Real Django runserver; optional, explicitly recorded application fault control."""
import argparse
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--note-loss", action="store_true")
args = parser.parse_args()
root = Path(args.project).resolve(strict=True)
sys.path[:0] = [str(root / ".acceptance-study"), str(root)]
os.environ["DJANGO_SETTINGS_MODULE"] = "study_settings"
import django
django.setup()
if args.note_loss:
    from django.db.models.signals import pre_save
    from bookmarks.models import Bookmark

    def lose_notes(sender, instance, **kwargs):
        # A deliberate local mutation control, never an alleged upstream bug.
        instance.notes = ""

    pre_save.connect(lose_notes, sender=Bookmark, weak=False)
from django.core.management import execute_from_command_line
execute_from_command_line(["manage.py", "runserver", "127.0.0.1:18741", "--noreload"])
