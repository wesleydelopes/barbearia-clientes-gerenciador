// main.js
document.addEventListener('DOMContentLoaded', function() {

    function isValidDate(dateString) {
        var regex = /^\d{2}-\d{2}-\d{4}$/;
        return dateString.match(regex);
    }
    // Função para carregar a lista de clientes usando AJAX
    function carregarListaClientes() {
        fetch('/get_clientes')
            .then(response => response.json())
            .then(clientes => {
                const tableBody = document.getElementById('clientesTableBody');
                tableBody.innerHTML = ''; // Limpar a tabela antes de adicionar novos clientes

                clientes.forEach(cliente => {
                    const newRow = document.createElement('tr');
                    newRow.innerHTML = `
                        <td>${cliente[0]}</td>
                        <td>${cliente[1]}</td>
                        <td>${cliente[2]}</td>
                        <td>${cliente[3]}</td>
                        <td>${isValidDate(cliente[4]) ? cliente[4] : 'Data Inválida'}</td>
                        <td>${cliente[5]}</td>
                        <td>${cliente[6] ? 'Sim' : 'Não'}</td>
                        <td>
                            <button class="btn btn-danger btn-sm" onclick="apagarCliente('${cliente[0]}')">Apagar</button>
                        </td>
                    `;
                    tableBody.appendChild(newRow);
                });
            })
            .catch(error => console.error('Erro ao carregar lista de clientes:', error));
    }

    // Função para apagar um cliente usando AJAX
    window.apagarCliente = function(nomeCliente) {
        fetch(`/apagar_cliente/${nomeCliente}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                carregarListaClientes(); // Recarregar a lista após apagar um cliente
            })
            .catch(error => console.error('Erro ao apagar cliente:', error));
            // Atualizar a página
            location.reload();
    }

    // Carregar a lista de clientes quando a página é carregada
    carregarListaClientes();
});
