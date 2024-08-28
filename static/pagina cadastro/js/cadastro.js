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
})

