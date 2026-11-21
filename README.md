# The Living Library widget

A searchable, sortable catalogue of the books PocketMFA writers have recommended in the
Living Library. It mirrors the Bookshop.org list at
https://bookshop.org/lists/the-living-library and links every title through PocketMFA's
Bookshop affiliate ID.

Live page (GitHub Pages): https://scottysegal727.github.io/living-library/

## Embed

Paste this where the widget should appear. The script sizes the frame to the widget's full
height, so the page has a single scrollbar and the widget never scrolls on its own:

```html
<iframe id="living-library" src="https://scottysegal727.github.io/living-library/"
        title="The Living Library" style="display:block;width:100%;height:1200px;border:0"></iframe>
<script>
(function(){
  var ORIGIN="https://scottysegal727.github.io";
  function frame(){return document.getElementById("living-library")}
  function hello(){var f=frame();if(f&&f.contentWindow)f.contentWindow.postMessage({ll:"hello"},ORIGIN)}
  window.addEventListener("message",function(e){
    var f=frame();if(e.origin!==ORIGIN||!f||e.source!==f.contentWindow)return;
    var d=e.data||{};
    if(d.ll==="ready")hello();
    else if(d.ll==="height"&&d.h>0)f.style.height=d.h+"px";
    else if(d.ll==="top"){var t=f.getBoundingClientRect().top;if(t<0)window.scrollBy({top:t-90,behavior:"smooth"})}
  });
  hello();
})();
</script>
```

Without the script the iframe still works; the widget then scrolls inside its own frame.

## Files

- `index.html` is the published widget. It is generated; do not edit it by hand.
- `src/template.html` holds the layout, styles and script.
- `data/books.json` has one record per book (ISBN, title, author, category, genres, subjects, publisher, year, pages, format, description, and `u`: the Living Library post URLs about it, newest first). The "See the library post" button opens the newest post; Circle shows it only to signed-in members.
- `data/covers.json` has small built-in cover thumbnails keyed by ISBN.
- `data/pending.json` lists books the weekly task added to the widget that still need re-checking and adding on the Bookshop list.
- `tools/add_books.py` adds or removes books from the data files.
- `tools/build.py` regenerates `index.html`.

## Updating

```sh
python3 tools/add_books.py new_books.json     # see the script header for the record format
python3 tools/add_books.py --remove 9780000000000
python3 tools/add_books.py --link 9780000000000 https://community.pocketmfa.com/c/the-living-library/post-slug   # new post about a book already listed
python3 tools/build.py
git add -A && git commit -m "Add new Living Library books" && git push
```

A weekly scheduled task does this automatically after it adds new books to the Bookshop list.
