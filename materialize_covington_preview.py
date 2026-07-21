#!/usr/bin/env python3
from __future__ import annotations

import base64
import io
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
bundle = root / '.covington-preview'
parts = sorted(bundle.glob('part-*.txt'))
if not parts:
    raise SystemExit('No preview parts found')
payload = base64.b64decode(''.join(p.read_text(encoding='ascii').strip() for p in parts))
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    for member in archive.infolist():
        target = (root / member.filename).resolve()
        if root not in target.parents and target != root:
            raise SystemExit(f'Unsafe path: {member.filename}')
    archive.extractall(root)
shutil.rmtree(bundle)
Path(__file__).unlink()
print('Covington review materialized.')
