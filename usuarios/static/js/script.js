document.addEventListener("DOMContentLoaded", function () {
  // Atualiza ano do rodapé
  const spanAno = document.getElementById("ano");
  if (spanAno) {
    spanAno.textContent = new Date().getFullYear();
  }

  // Validação de CNPJ (só se o campo existir na página)
  const cnpjInput = document.getElementById("cnpj");
  if (cnpjInput) {
    const regex = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/;
    cnpjInput.addEventListener("input", function () {
      if (!regex.test(this.value)) {
        this.setCustomValidity("CNPJ inválido. Use o formato 00.000.000/0000-00.");
      } else {
        this.setCustomValidity("");
      }
    });
  }

  // Habilitar/desabilitar botão "Unir Listas" (somente na página de listas)
  const btnUnir = document.getElementById("btn-unir");
  const checkboxes = document.querySelectorAll(".chk-lista");
  if (btnUnir && checkboxes.length) {
    const toggle = () => {
      btnUnir.disabled = document.querySelectorAll(".chk-lista:checked").length === 0;
    };
    checkboxes.forEach(chk => chk.addEventListener("change", toggle));
    toggle();
  }
});

// Carregar produtos por fornecedor (usado onde existe #produtos-container)
function carregarProdutos(fornecedorId) {
  const container = document.getElementById("produtos-container");
  if (!container) return; // garante que o elemento existe na página

  if (!fornecedorId) {
    container.innerHTML = "";
    return;
  }

  fetch(`/compras/produtos/${fornecedorId}/`)
    .then(response => response.text())
    .then(html => { container.innerHTML = html; })
    .catch(() => { container.innerHTML = "<p class='erro'>Falha ao carregar produtos.</p>"; });
}

// Edição de mínimo (só executa se encontrar os elementos)
function editarMinimo(id) {
  const texto = document.getElementById("minimo-text-" + id);
  const input = document.getElementById("minimo-input-" + id);
  const btnEditar = document.getElementById("btn-editar-" + id);
  const btnSalvar = document.getElementById("btn-salvar-" + id);

  if (texto && input && btnEditar && btnSalvar) {
    texto.style.display = "none";
    input.style.display = "inline-block";
    btnEditar.style.display = "none";
    btnSalvar.style.display = "inline-block";
    input.focus();
  }
}