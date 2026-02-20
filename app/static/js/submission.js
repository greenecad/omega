const dropZone = document.getElementById("drop-zone");

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