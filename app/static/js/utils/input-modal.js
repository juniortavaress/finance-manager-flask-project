document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("uploadModal");
  const addBtn = document.getElementById("add-btn");
  const closeBtn = modal ? modal.querySelector(".close") : null;
  const select = document.getElementById("dataTypeSelect");
  const uploadForm = document.getElementById("uploadForm");
  const folderSection = document.getElementById("folderSelection");
  const manualSection = document.getElementById("manualSection");

  if (!modal || !addBtn || !select || !uploadForm) {
    console.error("Algum elemento do modal não foi encontrado!");
    return;
  }

  // Abrir modal
  addBtn.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  // Fechar modal
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // Função para ativar/desativar required na seção manual
  const toggleRequired = (section, enable) => {
    section.querySelectorAll("input, select").forEach(el => {
      el.required = enable;
    });
  };

  // Mudar ação do formulário ao selecionar tipo
  select.addEventListener("change", (e) => {
    const value = e.target.value;

    const notesURL = uploadForm.dataset.uploadNotesUrl;
    const incomesURL = uploadForm.dataset.uploadIncomesUrl;
    const manualURL = uploadForm.dataset.manualEntryUrl;

    if (value === "manual_entry") {
      uploadForm.action = manualURL;
      folderSection.style.display = "none";
      manualSection.style.display = "block";
      toggleRequired(manualSection, true);
    } else if (value === "income_database") {
      uploadForm.action = incomesURL;
      folderSection.style.display = "block";
      manualSection.style.display = "none";
      toggleRequired(manualSection, false);
    } else {
      uploadForm.action = notesURL;
      folderSection.style.display = "block";
      manualSection.style.display = "none";
      toggleRequired(manualSection, false);
    }
  });

  // Log de arquivos selecionados
  const folderInput = folderSection.querySelector('input[type="file"]');
  if (folderInput) {
    folderInput.addEventListener("change", (e) => {
      console.log("Arquivos selecionados:", e.target.files);
    });
  }

  // Submissão do formulário
  uploadForm.addEventListener("submit", (e) => {
    console.log("Enviando formulário para:", uploadForm.action);
  });
});
