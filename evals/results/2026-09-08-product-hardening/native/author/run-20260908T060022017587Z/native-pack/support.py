"""Small native-test utilities for the pinned linkding study, not a Skill runner."""
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
import socket
import subprocess
import threading

PIN = "65813a75404b1319aca8b09700fadc0b15adabaf"
MAX_LOG = 1024 * 1024


def validate_project(project):
    root = Path(project).resolve(strict=True)
    if not (root / "manage.py").is_file():
        raise ValueError("Expected an isolated linkding checkout containing manage.py")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = subprocess.check_output(["git", "diff", "HEAD", "--name-only"], cwd=root, text=True)
    if head != PIN or dirty:
        raise ValueError("Expected the pinned, unmodified linkding source; preserve changes and use a fresh checkout")
    return root


def load_credentials(root):
    state = root / ".acceptance-study"
    private = state / "private.json"
    if any(path.is_symlink() for path in (state, private, state / "artifacts", state / "db.sqlite3")):
        raise ValueError("Study state and credentials must not be symlinks")
    if not (state / "artifacts").is_dir() or not (state / "db.sqlite3").is_file():
        raise ValueError("Study artifacts directory or database missing")
    if state.stat().st_mode & 0o077 or private.stat().st_mode & 0o077:
        raise ValueError("Study credentials must be readable only by their owner")
    value = json.loads(private.read_text())
    if (not isinstance(value, dict) or set(value) != {"django_secret", "users"}
            or not isinstance(value["users"], dict) or set(value["users"]) != {"fa_alice", "fa_bob"}):
        raise ValueError("Unexpected study credential format")
    if not all(isinstance(v, str) and len(v) >= 20 for v in [value["django_secret"], *value["users"].values()]):
        raise ValueError("Invalid study credentials")
    return value


def occupied(port):
    with socket.socket() as listener:
        listener.settimeout(.15)
        return listener.connect_ex(("127.0.0.1", port)) == 0


def publish_json(path, value):
    """Publish complete bytes without replacing prior evidence; caller owns parent."""
    path = Path(path)
    temporary = path.with_name(path.name + ".pending")
    created = False
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            created = True
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if created and temporary.exists():
            temporary.unlink()


class ProcessLogs:
    """Drain pipes, redact known study secrets, bound retained logs, join on stop."""
    def __init__(self, process, directory, name, secrets):
        self.threads = []
        self.errors = []
        self.truncated = []
        self.files = []
        for label, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
            path = directory / (name + "." + label + ".private.txt")
            self.files.append(path.name)
            thread = threading.Thread(target=self._drain, args=(pipe, path, secrets), daemon=True)
            thread.start()
            self.threads.append(thread)

    def _drain(self, pipe, path, secrets):
        # Capture at most MAX_LOG bytes before decoding so unbounded lines cannot
        # exhaust memory. Continue draining after the cap to avoid child deadlock.
        kept = bytearray()
        total = 0
        try:
            with pipe:
                while True:
                    part = pipe.read(8192)
                    if not part:
                        break
                    total += len(part)
                    kept.extend(part[:max(0, MAX_LOG - len(kept))])
            text = kept.decode("utf-8", errors="replace")
            for secret in sorted(secrets, key=len, reverse=True):
                text = text.replace(secret, "[REDACTED]")
            # A truncated suffix may be a partial secret: do not expose it.
            if total > MAX_LOG:
                text = text[:max(0, len(text) - max(map(len, secrets), default=1))]
                text += "\n[TRUNCATED; inspect locally with appropriate privacy controls]\n"
                self.truncated.append(path.name)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(text)
        except Exception as error:
            self.errors.append({"file": path.name, "error_type": type(error).__name__})

    def finish(self):
        for thread in self.threads:
            thread.join(timeout=5)
        if any(thread.is_alive() for thread in self.threads):
            self.errors.append({"error_type": "LogDrainIncomplete"})
        return {"files": self.files, "errors": self.errors, "truncated": self.truncated}


def classify(checks, obstacle, unresolved):
    """Only an observed assertion mismatch is business FAIL; setup is not one."""
    if any(value not in ("PASS", "FAIL", "UNVERIFIED") for value in checks.values()):
        obstacle = "invalid-check-status"
    failure = any(value == "FAIL" for value in checks.values())
    gap = not checks or any(value == "UNVERIFIED" for value in checks.values())
    verdict = "FAIL" if failure else ("UNVERIFIED" if gap or obstacle else "PASS")
    complete = not gap and obstacle is None and not unresolved
    return {"business_verdict": verdict, "qualified_pass": verdict == "PASS" and complete,
            "completion": "complete" if complete else "partial",
            "obstacle_kind": obstacle,
            "exit_code": 1 if failure else (0 if complete and verdict == "PASS" else 2)}


def inventory(directory):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(directory).iterdir()) if p.is_file() and p.suffix == ".py"}


def snapshot_pack(source, destination):
    """Freeze actual executable files; digests alone cannot reproduce old bytes."""
    destination.mkdir(mode=0o700)
    expected = inventory(source)
    for name in expected:
        with (destination / name).open('xb') as stream:
            stream.write((source / name).read_bytes())
    if inventory(destination) != expected or inventory(source) != expected:
        raise ValueError("Native pack changed while being captured")
    return expected


def environment_identity(root, pack):
    """Bind settings, article, locks and built assets; never read credentials."""
    pairs = [('study_settings.py', 'study_settings.py'), ('article/article.html', 'article.html')]
    for actual, template in pairs:
        path = root / '.acceptance-study' / actual
        if path.is_symlink() or path.read_bytes() != (pack / 'environment' / template).read_bytes():
            raise ValueError("Prepared environment differs from the reviewed template")
    paths = [root / 'uv.lock', root / 'package-lock.json',
             *(root / '.acceptance-study' / actual for actual, _ in pairs)]
    for directory in ('bookmarks/static', 'bookmarks/styles'):
        paths.extend(p for p in (root / directory).rglob('*') if p.is_file())
    if any(p.is_symlink() for p in paths):
        raise ValueError("Environment inputs must not be symlinks")
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def capture_allowed(page):
    """Conservatively omit login and Django debug 404/500 pages, not redact them."""
    if '/login' in urlsplit(page.url).path:
        return False
    return not page.locator('#traceback, #requestinfo, body > #explanation').count()


def initial_notes(run, case):
    notes = 'Private research notes ' + run + '\nSecond line: retain this context.'
    if case == 'unicode-notes':
        notes += '\n中文验收：保留原文、引号 "quoted"、emoji 🧭 和换行。'
    return notes
