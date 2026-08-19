/**
 * Aviso legal — Sinapesc REAP (interface desktop)
 * Copyright (c) Gabriel Lourran Da Silva Costa — uso proibido sem autorização.
 */
(function () {
  "use strict";
  var NOTICE =
    "© Gabriel Lourran Da Silva Costa · Software proprietário · " +
    "Proibido copiar, modificar ou redistribuir sem autorização · " +
    "gabriel730costa@gmail.com";
  function mount() {
    if (document.getElementById("legal-bar")) return;
    var bar = document.createElement("div");
    bar.id = "legal-bar";
    bar.className = "legal-bar";
    bar.textContent = NOTICE;
    document.body.appendChild(bar);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
