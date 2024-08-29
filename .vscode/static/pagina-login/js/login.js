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