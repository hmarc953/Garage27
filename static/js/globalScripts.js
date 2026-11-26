const navbarToggle = document.querySelector("#navbar-toggle");
const navbarLinks = document.querySelector(".navbar-links");
const navbarMenuLinks = document.querySelectorAll(".navbar-links a");
const navbarAccount = document.querySelector(".navbar-account");
const navbarCompact = window.matchMedia("(width < 450px)");
const navbarLoginButton = navbarAccount?.querySelector(".navbar-login-button");

if (navbarLinks && navbarLoginButton) {
    function moveNavbarAccount() {
        if (navbarCompact.matches) {
            navbarLinks.append(navbarAccount);
        } else {
            navbarLinks.after(navbarAccount);
        }
    }

    moveNavbarAccount();
    navbarCompact.addEventListener("change", moveNavbarAccount);
}

function closeNavbarMenu() {
    navbarLinks.classList.remove("active");
    navbarToggle.classList.remove("active");
    navbarToggle.setAttribute("aria-expanded", "false");
}

if (navbarToggle && navbarLinks) {
    navbarToggle.addEventListener("click", function() {
        const isOpen = navbarLinks.classList.toggle("active");

        navbarToggle.classList.toggle("active", isOpen);
        navbarToggle.setAttribute("aria-expanded", isOpen);
    });

    navbarMenuLinks.forEach(function(navbarLink) {
        navbarLink.addEventListener("click", closeNavbarMenu);
    });

    window.addEventListener("resize", function() {
        if (window.innerWidth > 650) {
            closeNavbarMenu();
        }
    });
}

const panelEliminarModal = document.querySelector("#panel-eliminar-modal");
const panelEliminarForm = document.querySelector("#panel-eliminar-form");

if (panelEliminarModal && panelEliminarForm) {
    document.querySelectorAll(".panel-eliminar-abrir").forEach(function(boton) {
        boton.addEventListener("click", function() {
            panelEliminarForm.action = boton.dataset.url;
            panelEliminarModal.showModal();
        });
    });

    panelEliminarModal.querySelectorAll("[data-cerrar-modal]").forEach(function(boton) {
        boton.addEventListener("click", function() {
            panelEliminarModal.close();
        });
    });

    panelEliminarModal.addEventListener("click", function(evento) {
        if (evento.target === panelEliminarModal) {
            panelEliminarModal.close();
        }
    });
}