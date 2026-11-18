#!/usr/bin/env python3
"""Rebuild index.html from src/template.html, data/books.json and data/covers.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
books = json.loads((root / "data/books.json").read_text(encoding="utf-8"))
covers = json.loads((root / "data/covers.json").read_text(encoding="utf-8"))
covers = {b["i"]: covers[b["i"]] for b in books if b["i"] in covers}
tpl = (root / "src/template.html").read_text(encoding="utf-8")
html = tpl.replace("__DATA__", json.dumps(books, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
html = html.replace("__COVERS__", json.dumps(covers, separators=(",", ":")))
(root / "index.html").write_text(html, encoding="utf-8")
print(f"built index.html: {len(books)} books, {len(covers)} built-in covers, {len(html):,} characters")
