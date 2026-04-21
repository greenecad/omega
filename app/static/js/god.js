let countdown = document.getElementById("countdown");
let text = document.getElementById("text");
let div = document.getElementById("div");
let timeLeft = 120;
let countdownInterval = setInterval(() => {
    timeLeft--;
    if (timeLeft <= 0) {
        clearInterval(countdownInterval);
        text.textContent = "GOD IS HERE";
        let timer = setTimeout(() => {
            countdown.style.display = 'none';
            /*let rain = document.createElement('img');
            rain.src = rainsrc;
            rain.classList.add('rain');
            document.body.appendChild(rain);*/
            document.body.style.backgroundImage = `url(${rainsrc})`;
            document.body.style.backgroundSize = 'cover';
            let code = document.createElement('p');
            code.textContent = '[[john 11:35]]';
            //document.body.appendChild(code);
            div.appendChild(code);
            let submitButton = document.getElementById('submit-button');
            if (submitButton) {
                submitButton.style.display = 'block';
            }
        }, 3000);
        
    }
    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;
    countdown.textContent = `${minutes}:${seconds}`;
}, 1000);