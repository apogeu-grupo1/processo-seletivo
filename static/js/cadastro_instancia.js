document.getElementById('submitCadastro').addEventListener('click', async function(e) {
    e.preventDefault();
    
    const formData = {
        //instancia_id: document.getElementById('instancia_id').value,
        livro_nome: document.getElementById('livro_nome').value,
        //genero_id: document.getElementById('genero_id').value,
        status: document.getElementById('status').value,
    };

    fetch('/cadastro_instancia', {  // URL do endpoint de cadastro
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.redirected) {
            // Se o backend redirecionar, isso detecta e redireciona o navegador
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else if (data.message) {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});
