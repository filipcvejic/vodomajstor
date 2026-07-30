/* VodoMajstor Beograd — minimalni JS. Mobilni meni i lightbox. Bez biblioteka. */
(function () {
  "use strict";

  /* --- Mobilni meni --- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("glavna-navigacija");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      toggle.setAttribute("aria-expanded", String(!open));
    });
  }

  /* --- Lightbox galerije (nativni <dialog>) --- */
  var gallery = document.querySelector("[data-gallery]");
  var dialog = document.getElementById("lightbox");

  if (gallery && dialog && typeof dialog.showModal === "function") {
    var target = dialog.querySelector("img");

    gallery.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      var img = btn.querySelector("img");
      if (!img) return;
      target.src = img.currentSrc || img.src;
      target.alt = img.alt;
      dialog.showModal();
    });

    dialog.addEventListener("click", function (e) {
      if (e.target === dialog || e.target.closest(".lightbox__close")) {
        dialog.close();
      }
    });
  }
})();
