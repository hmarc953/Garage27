const successModalButton = document.querySelector("#success-modal-button");
const successModalClose = document.querySelector("#success-modal-close");
const dateInput = document.querySelector("#id_fecha");
const formGroups = document.querySelectorAll(".form-group");
const workItems = document.querySelectorAll(".work-item");

workItems.forEach(function(workItem) {
    const workInfo = workItem.querySelector(".work-info");
    const closeButton = workItem.querySelector(".work-info-close");

    workItem.addEventListener("click", function() {
        workInfo.classList.add("active");
    });

    if (closeButton) {
        closeButton.addEventListener("click", function(event) {
            event.stopPropagation();
            workInfo.classList.remove("active");
        });
    }
});

if (successModalButton) {
    successModalButton.addEventListener("click", function() {
        window.location.href = "/";
    });
}

if (successModalClose) {
    successModalClose.addEventListener("click", function() {
        window.location.href = "/";
    });
}

if (dateInput) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    dateInput.min = `${year}-${month}-${day}`;
}

formGroups.forEach(function(formGroup) {
    const field = formGroup.querySelector("input, select, textarea");
    const errorList = formGroup.querySelector(".errorlist");

    if (field && errorList) {
        field.addEventListener("input", function() {
            errorList.remove();
        });

        field.addEventListener("change", function() {
            errorList.remove();
        });
    }
});

const turnoMarca = document.querySelector("#id_marca");
const turnoModelo = document.querySelector("#id_modelo");
const turnoListaMarcas = document.querySelector("#marcas-vehiculo");
const turnoListaModelos = document.querySelector("#modelos-vehiculo");

async function iniciarSugerenciasVehiculo() {
    const catalogoUrl = turnoListaModelos?.dataset.catalogoUrl;
    if (!turnoMarca || !turnoModelo || !turnoListaMarcas || !catalogoUrl) {
        return;
    }

    let catalogo;
    try {
        const respuesta = await fetch(catalogoUrl);
        if (!respuesta.ok) {
            return;
        }
        catalogo = Object.entries(await respuesta.json());
    } catch {
        return;
    }

    const marcas = catalogo.map(([marca]) => marca);
    const modelosPorMarca = new Map(catalogo.map(([marca, modelos]) => [marca.toLowerCase(), modelos]));

    function mostrarSugerencias(campo, lista, opciones) {
        const texto = campo.value.trim().toLowerCase();
        const coincidencias = texto
            ? opciones.filter(opcion => opcion.toLowerCase().startsWith(texto)).slice(0, 6)
            : [];

        lista.replaceChildren(...coincidencias.map(opcion => new Option(opcion, opcion)));

        if (coincidencias.length) {
            campo.setAttribute("list", lista.id);
        } else {
            campo.removeAttribute("list");
        }
    }

    function actualizarModelos() {
        const marca = turnoMarca.value.trim().toLowerCase();
        mostrarSugerencias(turnoModelo, turnoListaModelos, modelosPorMarca.get(marca) ?? []);
    }

    function actualizarMarca() {
        mostrarSugerencias(turnoMarca, turnoListaMarcas, marcas);
        actualizarModelos();
    }

    turnoMarca.addEventListener("input", actualizarMarca);
    turnoMarca.addEventListener("change", actualizarMarca);
    turnoModelo.addEventListener("input", actualizarModelos);
    actualizarMarca();
}

iniciarSugerenciasVehiculo();