document.addEventListener("DOMContentLoaded", function () {
  const anoAtual = new Date().getFullYear();
  const spanAno = document.getElementById("ano");
  if (spanAno) {
    spanAno.textContent = anoAtual;
  }
});