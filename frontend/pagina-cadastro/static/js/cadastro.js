var generosPreferidos = [];

function adicionarGenero(event){
    var botao = event.target;
    var genero = botao.innerText;
    
    if( generosPreferidos.includes(genero)){
        generosPreferidos = generosPreferidos.filter(g => g != genero);
        botao.classList.remove('selecionado');
    } else if (generosPreferidos.length < 3) {
        generosPreferidos.push(genero);
        botao.classList.add('selecionado');
    }

    console.log(generosPreferidos);
}

const inputFile = document.querySelector('.picture__input');
const pictureImage = document.querySelector('.picture__image');
const pictureImageTxt = "&#128100;";
pictureImage.innerHTML = pictureImageTxt;
inputFile.addEventListener('change', function(e){
    const inputTarget = e.target;
    const file = inputTarget.files[0];

    if(file){
        const reader = new FileReader();
        
        reader.addEventListener('load', function(e){
            const readerTarget = e.target;

            const img  = document.createElement('img');
            img.src = readerTarget.result;
            img.classList.add("picture__image");
            pictureImage.innerHTML = "";

            pictureImage.appendChild(img);
        })

        reader.readAsDataURL(file);
    } else{
        pictureImage.innerHTML = pictureImageTxt;
    }
});


const urlEstado = "https://servicodados.ibge.gov.br/api/v1/localidades/estados";
const cidade = document.getElementById("cidade");
const estado = document.getElementById("estado");

estado.addEventListener("change", async function(){
    const urlCidades = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/" +estado.value+ "/municipios";
    const request = await fetch(urlCidades);
    const response = await request.json();

    let options = "";
    response.forEach(function(cidades){
        options += "<option>" +cidades.nome+ "</option>";
    })

    cidade.innerHTML = options;
})

window.addEventListener("load", async function(){
    const request = await fetch(urlEstado);
    const response = await request.json();

    const options = document.createElement("optgroup");
    options.setAttribute("label", "Estados");
    response.forEach(function(estado){
        options.innerHTML += "<option value='" + estado.id + "'  data-nome='" + estado.nome + "'>" +estado.nome+ "</option>";
    })

    estado.append(options);
})



document.getElementById('submitButton').addEventListener('click', async function(e) {
    e.preventDefault();
    
    const fileInput = document.querySelector('.picture__input').files[0];
    let fotoCliente = null;

    if (fileInput) {
        fotoCliente = await getBase64(fileInput);
    }

    const formData = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        telefone: document.getElementById('telefone').value,
        username: document.getElementById('username').value,
        pais: document.getElementById('pais').value,
        estado: estado.options[estado.selectedIndex].getAttribute('data-nome'),
        cidade: document.getElementById('cidade').value,
        generosPreferidos: generosPreferidos.join(', '),
        fotoCliente: fotoCliente
    };

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error('Error:', error));
});

function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}
