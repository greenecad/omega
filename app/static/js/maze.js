let images= [];
for (let i=0; i< 7; i++) {
    images.push(document.getElementById(""+i));
}
let i = 0;
for(let image of images) {
    image.addEventListener('click', function() {
        image.style.display = 'none';
        images[(i+1) % images.length].style.display = 'flex';
        i = (i+1) % images.length;
        if (i === images.length - 1) {
            let text = document.createElement('p');
            text.textContent = "You see something on the floor..."
            text.style.fontSize = '24px';
            text.addEventListener('click', function() {
                text.textContent = "[[☞︎☜︎☜︎☹︎✋︎☠︎☝︎☹︎⚐︎💧︎❄︎]]";
                text.style.color = 'white';
                document.getElementById('submit-button').style.display = 'block';

            });
            document.querySelector('.frame').appendChild(text);
        }
        else if (i === 0) {
            let text = document.querySelector('.frame p');
            if (text) {
                text.remove();
            }
        }
    });
}