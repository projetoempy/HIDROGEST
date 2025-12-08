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