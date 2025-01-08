const gallery = document.querySelector(".masonry-grid");
const themeToggle = document.getElementById("theme-toggle");
const navLinks = document.querySelectorAll("nav a");
const sections = document.querySelectorAll("main > section");

let photos = [];
const isDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;

// Fetch photo list from API
async function fetchPhotoList() {
  try {
    const response = await fetch("/api/photo_list");
    photos = await response.json();
    loadImages();
  } catch (error) {
    console.error("Error fetching photo list:", error);
  }
}

// Function to load images
function loadImages() {
  photos.forEach((photo, index) => {
    const container = document.createElement("div");
    container.className = "masonry-item";

    const link = document.createElement("a");
    link.href = `/static/photos/${photo}`;
    link.setAttribute("data-fancybox", "gallery");

    const img = document.createElement("img");
    const src = `/static/photos/${photo}`;
    img.src = src.replace(".webp", "-thumbnail.webp");
    img.setAttribute("loading", "lazy");
    img.alt = `Photo ${index + 1}`;

    link.appendChild(img);
    container.appendChild(link);
    gallery.appendChild(container);
  });

  // Initialize Fancybox
  Fancybox.bind('[data-fancybox="gallery"]', {
    Toolbar: {
      display: {
        right: ["slideshow", "fullscreen", "thumbs", "close"],
      },
    },
  });
}

// Theme toggle
themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
});

// Navigation
navLinks.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    const targetSection = link.getAttribute("data-section");

    // Only update URL hash for "about" section, remove hash for gallery
    if (targetSection === "about") {
      window.location.hash = targetSection;
    } else {
      // Remove hash when clicking on Gallery
      history.pushState("", document.title, window.location.pathname);
    }

    switchSection(targetSection);
  });
});

// Function to switch sections
function switchSection(targetSection) {
  navLinks.forEach((l) => l.classList.remove("active"));
  document
    .querySelector(`[data-section="${targetSection}"]`)
    .classList.add("active");

  sections.forEach((section) => {
    if (section.id === targetSection) {
      section.classList.remove("hidden");
    } else {
      section.classList.add("hidden");
    }
  });
}

// Handle browser back/forward buttons
window.addEventListener("popstate", () => {
  const currentHash = window.location.hash.substring(1);
  const targetSection = currentHash || "gallery";
  switchSection(targetSection);
});

// Handle initial hash on page load
window.addEventListener("load", () => {
  const hash = window.location.hash.substring(1);
  const targetSection = hash === "about" ? "about" : "gallery";
  switchSection(targetSection);
});

// Initial load
fetchPhotoList();
if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
  document.body.classList.toggle("dark-mode");
}
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (event) => {
    document.body.classList.toggle("dark-mode", event.matches);
  });
