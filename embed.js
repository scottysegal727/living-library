/*
 * The Living Library: embed helper for the page that shows the widget.
 *
 * Use with:
 *   <iframe id="living-library" src="https://scottysegal727.github.io/living-library/"
 *           title="The Living Library" style="display:block;width:100%;height:2500px;border:0"></iframe>
 *   <script src="https://scottysegal727.github.io/living-library/embed.js"></script>
 *
 * It sizes the iframe to the widget's full height, so the page has one scrollbar and the
 * widget never scrolls on its own, and shows a "Back to search" button once the widget's
 * search bar has scrolled out of view. If this script does not load, the iframe still works
 * and the widget scrolls inside its frame.
 */
(function () {
  var ORIGIN = "https://scottysegal727.github.io";
  if (window.__livingLibraryEmbed) return;
  window.__livingLibraryEmbed = true;

  var barBottom = 0;
  var btn = null;

  function frame() {
    return document.getElementById("living-library") ||
      document.querySelector('iframe[src^="' + ORIGIN + '/living-library"]');
  }

  function post(msg) {
    var f = frame();
    if (f && f.contentWindow) f.contentWindow.postMessage(msg, ORIGIN);
  }

  function scrollToWidget() {
    var f = frame();
    if (!f) return;
    window.scrollTo({ top: f.getBoundingClientRect().top + window.pageYOffset - 20, behavior: "smooth" });
  }

  function updateButton() {
    var f = frame();
    if (!f || !btn || !barBottom) return;
    var r = f.getBoundingClientRect();
    var show = r.top + barBottom < 0 && r.bottom > window.innerHeight * 0.5;
    btn.classList.toggle("on", show);
  }

  function addButton() {
    var css = document.createElement("style");
    css.textContent =
      ".ll-back{position:fixed;right:24px;bottom:24px;z-index:99999;display:flex;align-items:center;gap:8px;" +
      "margin:0;padding:12px 20px;border:0;border-radius:999px;background:#133852;color:#fff;font-family:inherit;" +
      "font-size:15px;font-weight:600;line-height:1;letter-spacing:0;text-transform:none;" +
      "box-shadow:0 6px 18px rgba(0,0,0,.25);cursor:pointer;opacity:0;transform:translateY(12px);" +
      "pointer-events:none;transition:opacity .2s,transform .2s}" +
      ".ll-back.on{opacity:1;transform:none;pointer-events:auto}" +
      ".ll-back:hover{background:#0c2638}" +
      ".ll-back:focus-visible{outline:3px solid #dc2d3c;outline-offset:2px}" +
      ".ll-back svg{width:16px;height:16px;flex:none}" +
      "@media (max-width:600px){.ll-back{right:50%;bottom:18px;transform:translate(50%,12px)}" +
      ".ll-back.on{transform:translate(50%,0)}}";
    document.head.appendChild(css);

    btn = document.createElement("button");
    btn.type = "button";
    btn.className = "ll-back";
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">' +
      '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><span>Back to search</span>';
    btn.addEventListener("click", function () {
      scrollToWidget();
      // Put the cursor in the search box on computers; on phones that would pop up the keyboard.
      if (window.matchMedia && window.matchMedia("(pointer: fine)").matches) {
        setTimeout(function () { post({ ll: "focus" }); }, 450);
      }
    });
    document.body.appendChild(btn);
  }

  window.addEventListener("message", function (e) {
    var f = frame();
    if (e.origin !== ORIGIN || !f || e.source !== f.contentWindow) return;
    var d = e.data || {};
    if (d.ll === "ready") {
      post({ ll: "hello" });
    } else if (d.ll === "height" && d.h > 0) {
      f.style.height = d.h + "px";
      if (d.bar) barBottom = d.bar;
      updateButton();
    } else if (d.ll === "top") {
      if (f.getBoundingClientRect().top < 0) scrollToWidget();
    }
  });

  function start() {
    var f = frame();
    if (!f) return;
    if (!btn) addButton();
    f.addEventListener("load", function () { post({ ll: "hello" }); });
    post({ ll: "hello" });
  }

  window.addEventListener("scroll", updateButton, { passive: true });
  window.addEventListener("resize", updateButton);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
