async function setLanguage(lang) {
  try {
    const response = await fetch(`/static/lang/${lang}.json`);
    const texts = await response.json();

    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      const translation = texts[key];
      if (!translation) return;

      if (el.placeholder !== undefined) el.placeholder = translation;
      else if (el.tagName === 'INPUT' && el.type === 'button') el.value = translation;
      else el.innerText = translation;
    });

    localStorage.setItem("lang", lang);

    const selector = document.getElementById("language");
    if (selector) selector.value = lang;
  } catch (err) {
    console.error("Error loading language file:", err);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const savedLang = localStorage.getItem("lang") || "es";
  setLanguage(savedLang);
});
