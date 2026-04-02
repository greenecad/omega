
document.addEventListener('DOMContentLoaded', () => {
  const modals = Array.from(document.querySelectorAll('.modal'));
  if (modals.length === 0) return;
  let showIndex = 0;
  function show(i) {
    modals.forEach((m, idx) => m.style.display = idx === i ? 'block' : 'none');
  }
  modals.forEach((modal, i) => {
    const closes = modal.querySelectorAll('.close');
    closes.forEach(el => el.addEventListener('click', () => {
      modal.style.display = 'none';
      if (i + 1 < modals.length) show(i + 1);
    }));
    window.addEventListener('click', e => {
      if (e.target === modal) {
        modal.style.display = 'none';
        if (i + 1 < modals.length) show(i + 1);
      }
    });
  });
  show(showIndex);
});

let clickPoints=0;
let nextThreshold=0;
let points=0;
if (document.getElementById('clicker')) {
  let clicker = document.getElementById('clicker');
  let clicksP = clicker.nextElementSibling;
  let nextP = clicksP.nextElementSibling;
  let earnedP = nextP.nextElementSibling;
  
  let clicks = 0;
  clicker.addEventListener('click', function() {
    var btn = this;
    btn.disabled=true;
    btn.style.color = "gray";
    setTimeout(function(){
      btn.disabled = false;
      btn.style.color = "white";
    },200);
    clicks++;
    let nextPoints = nextThreshold - (clicks);
    if (nextPoints <= 0) {
      clicks = 0;
      clickPoints += 1;
      points += 10;
      nextThreshold = 2**clickPoints;
      nextP.textContent = `clicks to next ten points: ${nextThreshold}`;
    }
    clicksP.textContent = `Clicks: ${clicks}`;
    earnedP.textContent = `points earned: ${points}`;
    
  });
  document.querySelector('#clicker-form').addEventListener('submit', e => {
    if (clickPoints === 0) {
      e.preventDefault();
      alert('You have no points to cash in!');
    }
    let input = document.createElement('input');
    input.setAttribute('type', 'hidden');
    input.setAttribute('name', 'clickPoints');
    input.setAttribute('value', clickPoints);
    document.querySelector('#clicker-form').appendChild(input);
  });
}