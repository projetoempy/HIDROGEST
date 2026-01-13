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

// Botões de listas
  const btnUnir = document.getElementById("btn-unir");
  const btnEntregar = document.getElementById("btn-entregar");
  const checkboxes = document.querySelectorAll(".chk-lista");
  const selectAll = document.getElementById("select-all");

  function selecionadas() {
    return Array.from(checkboxes).filter(chk => chk.checked);
  }

  function atualizarBotoes() {
    const sel = selecionadas();
    if (btnUnir) btnUnir.disabled = false;            // sempre habilitado, backend valida
    if (btnEntregar) btnEntregar.disabled = sel.length === 0; // habilita se houver >= 1
  }

  if (checkboxes.length) {
    checkboxes.forEach(chk => chk.addEventListener("change", atualizarBotoes));
    atualizarBotoes();
  }

  if (selectAll) {
    selectAll.addEventListener("change", function () {
      checkboxes.forEach(chk => { chk.checked = selectAll.checked; });
      atualizarBotoes();
    });
  }

  // Ação do botão "Unir Listas" → mensagens pelo Django
  if (btnUnir) {
    btnUnir.addEventListener("click", function () {
      // Se nenhuma lista for marcada, o backend mostrará messages.error
      // O formulário será enviado vazio e tratado na view unir_listas
    });
  }

  // Ação do botão "Enviar Itens" → mensagens pelo Django
  if (btnEntregar) {
    btnEntregar.addEventListener("click", function (e) {
      e.preventDefault();
      const sel = selecionadas();

      if (sel.length === 0) {
        document.getElementById("lista_id").value = "";
        document.getElementById("form-entregar").submit();
        return;
      }

      if (sel.length > 1) {
        document.getElementById("lista_id").value = "MULTIPLAS";
        document.getElementById("form-entregar").submit();
        return;
      }

      document.getElementById("lista_id").value = sel[0].value;
      document.getElementById("form-entregar").submit();
    });
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