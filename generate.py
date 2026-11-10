#!/usr/bin/env python3
"""Generate explicitly labeled reference notes and synthetic dated history."""

import json
import os
from pathlib import Path
import random
import subprocess
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parent
NAME = "campank"
EMAIL = "npujiati430@gmail.com"
TOPICS = [
    ("pwd", "Menampilkan direktori kerja saat ini."),
    ("ls -lah", "Menampilkan daftar berkas termasuk berkas tersembunyi."),
    ("git status --short", "Memeriksa perubahan working tree secara ringkas."),
    ("git diff --stat", "Menampilkan ringkasan perubahan yang belum di-stage."),
    ("git log -5 --oneline", "Menampilkan lima commit terakhir secara ringkas."),
    ("df -h", "Memeriksa kapasitas filesystem dengan satuan mudah dibaca."),
    ("du -sh .", "Mengukur penggunaan disk direktori kerja."),
    ("python3 --version", "Memeriksa versi interpreter Python 3."),
    ("date -u", "Menampilkan waktu sekarang dalam UTC."),
    ("uname -s", "Menampilkan nama kernel sistem operasi."),
    ("printenv PATH", "Memeriksa direktori pencarian program executable."),
]


def git(*args, env=None):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, env=env, text=True
    ).strip()


def main():
    if git("config", "user.name") != NAME or git("config", "user.email") != EMAIL:
        raise SystemExit("Identitas Git lokal tidak cocok dengan akun tujuan.")
    if git("status", "--porcelain"):
        raise SystemExit("Working tree harus bersih sebelum generator dijalankan.")
    notes = ROOT / "notes"
    if notes.exists():
        raise SystemExit("Folder notes sudah ada; generator tidak dijalankan ulang.")
    notes.mkdir()
    rng = random.Random(1884192511)
    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    dates = sorted(today - timedelta(days=n) for n in rng.sample(range(1, 181), 121))
    for index, day in enumerate(dates, 1):
        command, description = TOPICS[(index - 1) % len(TOPICS)]
        note = notes / f"{index:03d}.md"
        note.write_text(
            f"# Kartu referensi {index:03d}\n\n"
            "> Dibuat otomatis sebagai contoh; tanggal commit bersifat sintetis.\n\n"
            f"```sh\n{command}\n```\n\n{description}\n",
            encoding="utf-8",
        )
        stamp = (day + timedelta(hours=12, minutes=rng.randrange(60))).isoformat()
        env = dict(os.environ, GIT_AUTHOR_NAME=NAME, GIT_AUTHOR_EMAIL=EMAIL,
                   GIT_COMMITTER_NAME=NAME, GIT_COMMITTER_EMAIL=EMAIL,
                   GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        git("add", "--", str(note.relative_to(ROOT)))
        git("commit", "-m", f"docs: generated CLI reference {index:03d}", env=env)
    print(json.dumps({"commits": int(git("rev-list", "--count", "HEAD")),
                      "author": f"{NAME} <{EMAIL}>",
                      "distinct_dates": len(set(git("log", "--format=%as").splitlines()))}))


if __name__ == "__main__":
    main()
