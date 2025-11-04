document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("uploadModal");
    const addBtn = document.getElementById("add-btn");
    const closeBtn = modal ? modal.querySelector(".close") : null;

    if (!modal || !addBtn) {
        console.error("Modal ou botão não encontrados no DOM");
        return;
    }

    // abrir modal
    addBtn.addEventListener("click", () => {
        modal.style.display = "flex";
    });

    // fechar modal
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });
    }

    // fechar clicando fora
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });
});
