/**
 * SmartFarm AI — Frontend Script
 * Handles form submission, API call to Flask backend,
 * and rendering of AI-generated farming advice.
 */

/* ---- Config ---- */
// When served by Flask (recommended), use a relative path so the
// request always goes to the same origin — no CORS / file:// issues.
const API_BASE = "";

/* ---- DOM references ---- */
const farmingForm     = document.getElementById("farmingForm");
const submitBtn       = document.getElementById("submitBtn");
const btnText         = document.getElementById("btnText");
const btnSpinner      = document.getElementById("btnSpinner");
const formError       = document.getElementById("form-error");
const formSuccess     = document.getElementById("form-success");

const adviceSection   = document.getElementById("advice-section");
const formSection     = document.getElementById("form-section");
const adviceFarmerName = document.getElementById("adviceFarmerName");
const adviceQuestion  = document.getElementById("adviceQuestion");
const adviceText      = document.getElementById("adviceText");
const askAnotherBtn   = document.getElementById("askAnotherBtn");
const resetBtn        = document.getElementById("resetBtn");

/* ===============================================
   HELPER: show / hide alert banners
   =============================================== */
function showAlert(el, message, show = true) {
  el.textContent = message;
  el.classList.toggle("d-none", !show);
}

/* ===============================================
   HELPER: toggle loading state on submit button
   =============================================== */
function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  btnText.classList.toggle("d-none", isLoading);
  btnSpinner.classList.toggle("d-none", !isLoading);
}

/* ===============================================
   HELPER: format raw AI text into HTML
   Converts markdown-like **bold** and bullet "-" lines
   =============================================== */
function formatAdvice(text) {
  // Replace **text** with <strong>
  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Convert lines starting with "-" to bullet list items
  const lines = text.split("\n");
  let inList = false;
  let html = "";
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("- ")) {
      if (!inList) { html += "<ul class='mb-2 ps-3'>"; inList = true; }
      html += `<li>${trimmed.slice(2)}</li>`;
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      if (trimmed === "") {
        html += "<br/>";
      } else {
        html += `<p class='mb-1'>${trimmed}</p>`;
      }
    }
  }
  if (inList) html += "</ul>";
  return html;
}

/* ===============================================
   SCROLL to section smoothly
   =============================================== */
function scrollTo(sectionId) {
  document.getElementById(sectionId).scrollIntoView({ behavior: "smooth" });
}

/* ===============================================
   FORM SUBMIT handler
   =============================================== */
farmingForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  e.stopPropagation();

  // Hide previous alerts
  showAlert(formError, "", false);
  showAlert(formSuccess, "", false);

  // Bootstrap validation
  if (!farmingForm.checkValidity()) {
    farmingForm.classList.add("was-validated");
    return;
  }
  farmingForm.classList.remove("was-validated");

  // Gather form data
  const payload = {
    farmerName : document.getElementById("farmerName").value.trim(),
    location   : document.getElementById("location").value.trim(),
    crop       : document.getElementById("crop").value.trim(),
    soilType   : document.getElementById("soilType").value,
    season     : document.getElementById("season").value,
    question   : document.getElementById("question").value.trim(),
  };

  // Start loading
  setLoading(true);

  try {
    const response = await fetch(`${API_BASE}/advice`, {
      method  : "POST",
      headers : { "Content-Type": "application/json" },
      body    : JSON.stringify(payload),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Server error ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Unknown error from server.");
    }

    /* --- Show advice section --- */
    adviceFarmerName.textContent = payload.farmerName;
    adviceQuestion.textContent   = payload.question;
    adviceText.innerHTML         = formatAdvice(data.advice);

    // Hide form, show advice
    formSection.classList.add("d-none");
    adviceSection.classList.remove("d-none");
    scrollTo("advice-section");

  } catch (err) {
    showAlert(formError, `❌ ${err.message}`, true);
    console.error("API error:", err);
  } finally {
    setLoading(false);
  }
});

/* ===============================================
   RESET button — clear validation state
   =============================================== */
resetBtn.addEventListener("click", () => {
  farmingForm.classList.remove("was-validated");
  showAlert(formError, "", false);
  showAlert(formSuccess, "", false);
});

/* ===============================================
   ASK ANOTHER QUESTION — go back to form
   =============================================== */
askAnotherBtn.addEventListener("click", () => {
  adviceSection.classList.add("d-none");
  formSection.classList.remove("d-none");
  farmingForm.reset();
  farmingForm.classList.remove("was-validated");
  scrollTo("form-section");
});
