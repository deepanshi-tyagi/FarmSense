document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("predictionForm");
    const loadingBox = document.getElementById("loadingBox");

    if (form) {
        form.addEventListener("input", validateInputsLive);

        form.addEventListener("submit", function (event) {
            const isValid = validateInputsLive();

            if (!isValid) {
                event.preventDefault();
                return;
            }

            loadingBox.classList.remove("d-none");
        });
    }

    const savedLanguage = localStorage.getItem("farmsense_language") || "en";
    setLanguage(savedLanguage);

    revealOnScroll();
    window.addEventListener("scroll", revealOnScroll);
    initializeAssistant();
});


function initializeAssistant() {
    const toggle = document.getElementById("assistantToggle");
    const panel = document.getElementById("assistantPanel");
    const close = document.getElementById("assistantClose");
    const form = document.getElementById("assistantForm");
    const input = document.getElementById("assistantInput");
    const messages = document.getElementById("assistantMessages");
    if (!toggle || !panel || !form) return;

    const setOpen = (open) => {
        panel.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        if (open) input.focus();
    };

    toggle.addEventListener("click", () => setOpen(panel.hidden));
    close.addEventListener("click", () => setOpen(false));

    const addMessage = (text, sender) => {
        const bubble = document.createElement("div");
        bubble.className = `assistant-message ${sender}`;
        bubble.textContent = text;
        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
        return bubble;
    };

    const ask = async (question) => {
        const cleanQuestion = question.trim();
        if (!cleanQuestion) return;
        addMessage(cleanQuestion, "user");
        input.value = "";
        const waiting = addMessage("Thinking...", "bot waiting");

        try {
            const response = await fetch("/api/assistant", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: cleanQuestion })
            });
            const data = await response.json();
            waiting.textContent = response.ok ? data.reply : (data.error || "Please try again.");
        } catch (error) {
            waiting.textContent = "The assistant is unavailable. Please check that FarmSense is running.";
        }
        waiting.classList.remove("waiting");
    };

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        ask(input.value);
    });
    panel.querySelectorAll("[data-question]").forEach((button) => {
        button.addEventListener("click", () => ask(button.dataset.question));
    });
}


function validateInputsLive() {
    const validationBox = document.getElementById("validationBox");

    const N = Number(document.querySelector("[name='N']").value);
    const P = Number(document.querySelector("[name='P']").value);
    const K = Number(document.querySelector("[name='K']").value);
    const ph = Number(document.querySelector("[name='ph']").value);
    const rainfall = Number(document.querySelector("[name='rainfall']").value);

    let errors = [];

    if (N < 0) errors.push("Nitrogen cannot be negative.");
    if (P < 0) errors.push("Phosphorus cannot be negative.");
    if (K < 0) errors.push("Potassium cannot be negative.");
    if (rainfall < 0) errors.push("Rainfall cannot be negative.");

    if (ph < 0 || ph > 14) {
        errors.push("pH value must be between 0 and 14.");
    }

    if (N > 200) errors.push("Nitrogen value looks too high.");
    if (P > 200) errors.push("Phosphorus value looks too high.");
    if (K > 200) errors.push("Potassium value looks too high.");
    if (rainfall > 500) errors.push("Rainfall value looks too high.");

    if (errors.length > 0) {
        validationBox.classList.remove("d-none");
        validationBox.innerHTML = errors.map(error => `<p>⚠️ ${error}</p>`).join("");
        return false;
    }

    validationBox.classList.add("d-none");
    validationBox.innerHTML = "";
    return true;
}


function fillRandom() {
    const cities = ["Delhi", "Mumbai", "Kolkata", "Bangalore", "Chennai", "Jaipur"];
    const soils = ["Loamy", "Sandy", "Clay", "Black", "Alluvial"];
    const seasons = ["Kharif", "Rabi", "Summer", "Winter", "All season"];
    const irrigation = ["yes", "no"];

    document.querySelector("[name='city']").value = cities[Math.floor(Math.random() * cities.length)];
    document.querySelector("[name='N']").value = Math.floor(Math.random() * 120);
    document.querySelector("[name='P']").value = Math.floor(Math.random() * 100);
    document.querySelector("[name='K']").value = Math.floor(Math.random() * 100);
    document.querySelector("[name='ph']").value = (5 + Math.random() * 3).toFixed(1);
    document.querySelector("[name='rainfall']").value = Math.floor(Math.random() * 250);

    document.querySelector("[name='soil_type']").value = soils[Math.floor(Math.random() * soils.length)];
    document.querySelector("[name='season']").value = seasons[Math.floor(Math.random() * seasons.length)];
    document.querySelector("[name='irrigation']").value = irrigation[Math.floor(Math.random() * irrigation.length)];

    validateInputsLive();
}


function toggleLanguage() {
    const currentLanguage = localStorage.getItem("farmsense_language") || "en";
    const newLanguage = currentLanguage === "en" ? "hi" : "en";

    localStorage.setItem("farmsense_language", newLanguage);
    setLanguage(newLanguage);
}


function setLanguage(language) {
    const elements = document.querySelectorAll("[data-en][data-hi]");

    elements.forEach((element) => {
        element.textContent = element.getAttribute(`data-${language}`);
    });

    updatePlaceholders(language);
}


function updatePlaceholders(language) {
    const translations = {
        en: {
            city: "Enter City e.g. Delhi",
            N: "Nitrogen",
            P: "Phosphorus",
            K: "Potassium",
            ph: "pH Value",
            rainfall: "Rainfall"
        },
        hi: {
            city: "शहर दर्ज करें जैसे Delhi",
            N: "नाइट्रोजन",
            P: "फॉस्फोरस",
            K: "पोटैशियम",
            ph: "pH मान",
            rainfall: "वर्षा"
        }
    };

    Object.keys(translations[language]).forEach((name) => {
        const input = document.querySelector(`[name='${name}']`);
        if (input) {
            input.placeholder = translations[language][name];
        }
    });
}


function revealOnScroll() {
    const cards = document.querySelectorAll(".premium-card");

    cards.forEach((card) => {
        const cardTop = card.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if (cardTop < windowHeight - 80) {
            card.classList.add("fade-up");
        }
    });
}
