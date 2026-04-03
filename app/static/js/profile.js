
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

const dropZone = document.getElementById("drop-zone");

if(dropZone){
  dropZone.addEventListener("drop", dropHandler);

  window.addEventListener("drop", (e) => {
    if ([...e.dataTransfer.items].some((item) => item.kind === "file")) {
      e.preventDefault();
    }
  });

  dropZone.addEventListener("dragover", (e) => {
    const fileItems = [...e.dataTransfer.items].filter(
      (item) => item.kind === "file",
    );
    if (fileItems.length > 0) {
      e.preventDefault();
      if (fileItems.some((item) => item.type.startsWith("image/"))) {
        e.dataTransfer.dropEffect = "copy";
      } else {
        e.dataTransfer.dropEffect = "none";
      }
    }
  });

  window.addEventListener("dragover", (e) => {
    const fileItems = [...e.dataTransfer.items].filter(
      (item) => item.kind === "file",
    );
    if (fileItems.length > 0) {
      e.preventDefault();
      if (!dropZone.contains(e.target)) {
        e.dataTransfer.dropEffect = "none";
      }
    }
  });

  const preview = document.getElementById("preview");

  function displayImages(files) {
    if (preview.children.length > 0) {
    for (const img of preview.querySelectorAll("img")) {
      URL.revokeObjectURL(img.src);
    }
    preview.textContent = "";
    // Also clear the underlying file input so the files are removed from the form
    if (fileInput) {
      try {
        fileInput.value = "";
      } catch (err) {
        // Some browsers may throw when resetting files; fallback by replacing the input
        const newInput = fileInput.cloneNode(true);
        newInput.addEventListener("change", (e) => displayImages(e.target.files));
        fileInput.parentNode.replaceChild(newInput, fileInput);
        fileInput = newInput;
      }
    }
    }
    let file= files[0];
    if (file.type.startsWith("image/")) {
      const li = document.createElement("li");
      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      img.alt = file.name;
      li.appendChild(img);
      li.appendChild(document.createTextNode(file.name));
      preview.appendChild(li);
    }
  }

  function dropHandler(ev) {
    ev.preventDefault();
    let files = [...ev.dataTransfer.items]
    files = files[0]
      .map((item) => item.getAsFile())
      .filter((file) => file);
    displayImages(files);
  }

  let fileInput = document.getElementById("file-input");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      displayImages(e.target.files);
    });
  }

  const clearBtn = document.getElementById("clear-btn");
  clearBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    for (const img of preview.querySelectorAll("img")) {
      URL.revokeObjectURL(img.src);
    }
    preview.textContent = "";
    // Also clear the underlying file input so the files are removed from the form
    if (fileInput) {
      try {
        fileInput.value = "";
      } catch (err) {
        // Some browsers may throw when resetting files; fallback by replacing the input
        const newInput = fileInput.cloneNode(true);
        newInput.addEventListener("change", (e) => displayImages(e.target.files));
        fileInput.parentNode.replaceChild(newInput, fileInput);
        fileInput = newInput;
      }
    }
  });
}