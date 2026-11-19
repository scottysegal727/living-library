#!/usr/bin/env python3
"""Add or replace books in data/books.json.

Usage: python3 tools/add_books.py new_books.json [--remove ISBN ...]
       python3 tools/add_books.py --link ISBN POST_URL
         (adds a Living Library post link to a book already in the widget; the newest
          link is shown first, so pass the post the button should open)

new_books.json is a JSON array of raw records read from each book's Bookshop.org
product page:
  {"isbn": "978...", "name": "Title", "authors": ["First Author", ...],
   "shelves": [["Poetry", "/categories/m/fiction/poetry"],
               ["American - General", "/categories/bisac/poe/005010"]],
   "pub": "Publisher", "date": "2011-03-01", "pages": 224,
   "fmt": "Paperback", "desc": "First ~320 characters of the description",
   "cover": "<optional base64 WebP/JPEG thumbnail, about 180px tall>",
   "category": "<optional override: one of CATEGORIES>",
   "genres": ["<optional: broad shelf names, e.g. Poetry, Literary Fiction>"],
   "topics": ["<optional: subject names, e.g. Coming of Age>"],
   "post_url": "<the Circle post about this book, https://community.pocketmfa.com/c/the-living-library/...>"}

When the shelf links are not available (for example when the page was read as text),
leave "shelves" out and give "category", "genres" and "topics" instead.
"""
import html, json, pathlib, re, sys

CATEGORIES = ["Fiction", "Short Stories", "Poetry", "Memoir & Biography",
              "Essays & Nonfiction", "Craft & Criticism", "Plays & Graphic Works"]
SKIP_TOPICS = {"Reference", "Music", "Health", "Psychology"}
root = pathlib.Path(__file__).resolve().parent.parent


def clean_topic(n):
    n = re.sub(r"\s*\((single author|multiple authors)\)", "", n)
    n = re.sub(r"\s*-\s*General$", "", n)
    n = n.replace("Subjects & Themes - ", "").replace("Writing - ", "Writing: ")
    return n.replace("Nonfiction (Incl. Memoirs)", "Nonfiction & Memoir").strip()


def clean_title(t):
    t = html.unescape(t)
    t = re.sub(r"\s*[\(\[][^\)\]]*(Winner|Book Club|Edition|Book \d|Pick)[^\)\]]*[\)\]]", "", t)
    t = re.sub(r":\s*(Oprah's Book Club|A Read with Jenna Pick).*$", "", t)
    return t.strip().strip('"')


def categorise(names, pre):
    first = pre[0] if pre else ""
    craftish = first in ("lan", "lit", "ref", "per") or "lan" in pre or "Creativity" in names
    if first == "poe":
        return "Poetry"
    if craftish and first not in ("fic", "yaf", "juv"):
        return "Craft & Criticism"
    if first in ("fic", "yaf", "juv"):
        return "Short Stories" if any("Short Stories" in n for n in names) else "Fiction"
    if "bio" in pre:
        return "Memoir & Biography"
    if first in ("cgn", "dra"):
        return "Plays & Graphic Works"
    if "poe" in pre:
        return "Poetry"
    if "fic" in pre:
        return "Fiction"
    return "Essays & Nonfiction"


def shape(b):
    shelves = b.get("shelves") or []
    bis = [(n, h.split("/bisac/")[1].split("/")[0]) for n, h in shelves
           if "/bisac/" in h and "/" in h.split("/bisac/")[1]]
    names = [n for n, _ in bis]
    pre = [p for _, p in bis]
    topics = []
    for n in names:
        c = clean_topic(n)
        if c and c not in topics and c not in SKIP_TOPICS:
            topics.append(c)
    authors = b.get("authors") or ["Unknown"]
    a0 = html.unescape(re.sub(r"^(Professor|Author|Dr\.?)\s+", "", authors[0]))
    if b.get("topics"):
        topics = [clean_topic(t) for t in b["topics"] if clean_topic(t) not in SKIP_TOPICS]
    cat = b.get("category") or categorise(names, pre)
    if cat not in CATEGORIES:
        raise SystemExit(f"unknown category {cat!r} for {b['isbn']}")
    fmt = (b.get("fmt") or "Paperback").split("/")[-1]
    urls = [u for u in ([b.get("post_url")] + list(b.get("post_urls") or [])) if u]
    for u in urls:
        if not u.startswith("https://community.pocketmfa.com/"):
            raise SystemExit(f"post_url must be a community.pocketmfa.com link, got {u!r}")
    return dict(i=b["isbn"], t=clean_title(b["name"]), a=a0, n=len(authors), c=cat, u=urls,
                g=b.get("genres") or [n for n, h in shelves if "/bisac/" not in h], k=topics,
                p=b.get("pub") or "", y=int((b.get("date") or "0")[:4] or 0),
                pg=b.get("pages") or 0, f={"EBook": "Ebook"}.get(fmt, fmt),
                d=html.unescape(b.get("desc") or "")[:320])


def main():
    args = sys.argv[1:]
    if args[:1] == ["--link"]:
        if len(args) != 3:
            raise SystemExit("usage: --link ISBN POST_URL")
        isbn, url = args[1], args[2]
        if not url.startswith("https://community.pocketmfa.com/"):
            raise SystemExit("POST_URL must be a community.pocketmfa.com link")
        books = json.loads((root / "data/books.json").read_text(encoding="utf-8"))
        hit = [x for x in books if x["i"] == isbn]
        if not hit:
            raise SystemExit(f"no book with ISBN {isbn}")
        hit[0]["u"] = [url] + [u for u in hit[0].get("u", []) if u != url]
        (root / "data/books.json").write_text(json.dumps(books, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print("linked", isbn, hit[0]["t"], "->", url)
        return
    remove = set()
    if "--remove" in args:
        i = args.index("--remove")
        remove = set(args[i + 1:])
        args = args[:i]
    books = json.loads((root / "data/books.json").read_text(encoding="utf-8"))
    covers = json.loads((root / "data/covers.json").read_text(encoding="utf-8"))
    new = json.loads(pathlib.Path(args[0]).read_text(encoding="utf-8")) if args else []
    for b in new:
        if not re.fullmatch(r"97[89]\d{10}", b["isbn"]):
            raise SystemExit(f"bad ISBN {b['isbn']!r}")
        rec = shape(b)
        old = [x for x in books if x["i"] == rec["i"]]
        if old:
            rec["u"] = rec["u"] + [u for u in old[0].get("u", []) if u not in rec["u"]]
        books = [x for x in books if x["i"] != rec["i"]] + [rec]
        if b.get("cover"):
            covers[rec["i"]] = b["cover"]
        print("added", rec["i"], rec["t"], "-", rec["a"], "[" + rec["c"] + "]")
    books = [x for x in books if x["i"] not in remove]
    for r in remove:
        covers.pop(r, None)
    (root / "data/books.json").write_text(json.dumps(books, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (root / "data/covers.json").write_text(json.dumps(covers, separators=(",", ":")), encoding="utf-8")
    print(len(books), "books")


if __name__ == "__main__":
    main()
