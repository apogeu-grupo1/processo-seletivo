document.getElementById('submitLogin').addEventListener('click', async function(e) {
    e.preventDefault();
    
    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.redirected) {
            // Se o backend redirecionar, o navegador é redirecionado
            window.location.href = response.url;
            return;  // Pare a execução aqui se houver redirecionamento
        } else if (response.ok) {
            return response.json();
        } else {
            // Se a resposta for 400 ou 500, a resposta é tratada como erro
            return response.text().then(text => {
                throw new Error(text || response.statusText);
            });
        }
    })

    .then(data => {
        if (data && data.error) {
            alert(data.error);
        } else if (data && data.message) {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocorreu um erro ao fazer login. Por favor, tente novamente.');
    })
});