/* ==========================================================================
   JobShield AI - shared front-end behaviour
   --------------------------------------------------------------------------
   Everything here improves usability only. The server always re-checks every
   value, so disabling JavaScript can never let bad data through.

   This file is loaded from our own domain only, which keeps the strict
   Content-Security-Policy (no inline script) happy.
   ========================================================================== */

(function () {
  "use strict";

  /* ---------------------------------------------------- Mobile navigation -- */
  var navToggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");

  function closeNav() {
    if (!navToggle || !nav) return;
    navToggle.setAttribute("aria-expanded", "false");
    nav.setAttribute("data-open", "false");
  }

  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var isOpen = navToggle.getAttribute("aria-expanded") === "true";
      navToggle.setAttribute("aria-expanded", String(!isOpen));
      nav.setAttribute("data-open", String(!isOpen));
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && navToggle.getAttribute("aria-expanded") === "true") {
        closeNav();
        navToggle.focus();
      }
    });
  }

  /* -------------------------------------------------- Character counters -- */
  document.querySelectorAll("[data-counter-target]").forEach(function (field) {
    var key = field.getAttribute("data-counter-target");
    var output = document.querySelector('[data-counter="' + key + '"]');
    if (!output) return;

    var max = field.getAttribute("maxlength") || "";

    function refresh() {
      output.textContent = field.value.length + " / " + max + " characters";
    }

    field.addEventListener("input", refresh);
    refresh();
  });

  /* --------------------------------------------------------- Analysis form -- */
  var form = document.querySelector("[data-analyze-form]");
  if (!form) return;

  var submitButton = form.querySelector("[data-submit-button]");
  var loadingMessage = form.querySelector("[data-loading-message]");
  var errorRegion = form.querySelector("[data-form-error]");

  // The same limits the server enforces. Think of this as a courtesy check:
  // it saves you a round trip, it does not replace the server's own checks.
  var RULES = [
    { id: "job_title", label: "Job title", min: 3, max: 200 },
    { id: "job_description", label: "Job description", min: 50, max: 15000 }
  ];

  function showError(message) {
    if (!errorRegion) return;
    errorRegion.textContent = message;
    errorRegion.hidden = false;
  }

  function clearError() {
    if (!errorRegion) return;
    errorRegion.textContent = "";
    errorRegion.hidden = true;
  }

  form.addEventListener("submit", function (event) {
    clearError();

    for (var i = 0; i < RULES.length; i++) {
      var rule = RULES[i];
      var field = document.getElementById(rule.id);
      if (!field) continue;

      var value = field.value.trim();
      var problem = "";

      if (value.length === 0) {
        problem = rule.label + " is required.";
      } else if (value.length < rule.min) {
        problem =
          rule.label + " must be at least " + rule.min + " characters (currently " +
          value.length + ").";
      } else if (value.length > rule.max) {
        problem = rule.label + " must be at most " + rule.max + " characters.";
      }

      if (problem) {
        event.preventDefault();
        showError(problem);
        field.focus();
        return;
      }
    }

    // Everything looks reasonable - lock the button so it cannot be sent twice.
    if (submitButton) {
      submitButton.setAttribute("aria-disabled", "true");
      submitButton.disabled = true;
      var spinner = submitButton.querySelector("[data-spinner]");
      if (spinner) spinner.hidden = false;
      var label = submitButton.querySelector(".btn__label");
      if (label) label.textContent = "Analyzing…";
    }
    if (loadingMessage) {
      loadingMessage.textContent = "Analyzing the job posting. Please wait…";
    }
  });
})();
