var currentTab = 0; // Current tab is set to be the first tab (0)
showTab(currentTab); // Display the current tab

function showTab(n) {
  // This function will display the specified tab of the form...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  //... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
  }
  if (n == (x.length - 1)) {
    document.getElementById("nextBtn").innerHTML = "Submit";
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
  }
  //... and run a function that will display the correct step indicator:
  fixStepIndicator(n)
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // if you have reached the end of the form...
  if (currentTab >= x.length) {
    // ... the form gets submitted:
    if (!document.getElementsByName("terms")[0].checked) {
      alert("You must agree to the terms and conditions! I'm trying to not get in trouble here...");
      currentTab = 5;
      showTab(currentTab);
      return false;
    }
    if(document.getElementsByName("id_image")[0].value == "" && !document.getElementsByName("id_later")[0].checked) {
      alert("You must upload a student ID or select that you will upload it later!");
      currentTab = 3;
      showTab(currentTab);
      return false;
    }
    if (document.getElementsByName("password")[0].value != document.getElementsByName("confirm_password")[0].value) {
      alert("Passwords do not match!");
      currentTab = 5;
      showTab(currentTab);
      return false;
    }
    if(!document.getElementsByName("email")[0].value.endsWith("@studentmail.conroeisd.net")) {
      alert("please enter a valid school email address!");
      currentTab = 4;
      showTab(currentTab);
      return false;
    }
    document.getElementById("regForm").submit();
    return false;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
  // This function deals with validation of the form fields
  var x, y, i, valid = true;
  x = document.getElementsByClassName("tab");
  y = x[currentTab].getElementsByTagName("input");
  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
    // If a field is empty...
    if (y[i].value == "" && y[i].name != "id_image" && y[i].name != "id_later") {
      // add an "invalid" class to the field:
      y[i].className += " invalid";
      // and set the current valid status to false
      valid = false;
    }
  }
  var contains_radio= false;
  var radio_valid = true;
  for (i = 0; i < y.length; i++) {
    // If a field is empty...
    if (y[i].type == "radio") {
      contains_radio= true;
    }
  }
  if (contains_radio){
    radio_valid = [...y].some((input) => input.type === "radio" && input.checked);
  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid && radio_valid) {
    document.getElementsByClassName("step")[currentTab].className += " finish";
  }
  return valid && radio_valid; // return the valid status
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class on the current step:
  x[n].className += " active";
}

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

function popUpToggle(num) {
  var popup = document.getElementById("popup" + num);
  popup.classList.toggle("show");
  for (let i = 1; i<=7; i++){
    if (i != num && document.getElementById('popup'+i).classList.contains("show")) {
      document.getElementById('popup'+i).classList.toggle("show")
    }
  }
}