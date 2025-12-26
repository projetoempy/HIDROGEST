document.addEventListener("DOMContentLoaded", function () {
  const anoAtual = new Date().getFullYear();
  const spanAno = document.getElementById("ano");
  if (spanAno) {
    spanAno.textContent = anoAtual;
  }
});

function carregarProdutos(fornecedorId) {
  if (!fornecedorId) {
    document.getElementById('produtos-container').innerHTML = '';
    return;
  }

  fetch(`/compras/produtos/${fornecedorId}/`)
    .then(response => response.text())
    .then(html => {
      document.getElementById('produtos-container').innerHTML = html;
    });
}

function editarMinimo(id) {
  const texto = document.getElementById('minimo-text-' + id);
  const input = document.getElementById('minimo-input-' + id);
  const btnEditar = document.getElementById('btn-editar-' + id);
  const btnSalvar = document.getElementById('btn-salvar-' + id);

  if (texto && input && btnEditar && btnSalvar) {
    texto.style.display = 'none';
    input.style.display = 'inline-block';
    btnEditar.style.display = 'none';
    btnSalvar.style.display = 'inline-block';
    input.focus();
  }
}

document.getElementById("cnpj").addEventListener("input", function() {
  const regex = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/;
  if (!regex.test(this.value)) {
    this.setCustomValidity("CNPJ inválido. Use o formato 00.000.000/0000-00.");
  } else {
    this.setCustomValidity("");
  }
});
