const textInput = document.querySelector("#textInput");

function loadTextInputHeight() {
    const savedHeight = localStorage.getItem("textInputHeight");

    if (savedHeight) {
        textInput.style.height = savedHeight;
    }
}

function saveTextInputHeight() {
    localStorage.setItem("textInputHeight", textInput.style.height);
}

loadTextInputHeight();

const resizeObserver = new ResizeObserver(() => {
    saveTextInputHeight();
});
resizeObserver.observe(textInput);