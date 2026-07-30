/* VodoMajstor Beograd — minimalni JS.
   Mobilni meni, lightbox za galeriju, blagi ulaz sekcija. Bez biblioteka. */
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

  /* --- Blagi ulaz sekcija --- */
  var reveals = document.querySelectorAll(".reveal");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reveals.length && !reduced && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });

    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }
})();
