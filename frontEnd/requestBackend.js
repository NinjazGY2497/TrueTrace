const imageInput = document.querySelector("#imageInput");
const textInput = document.querySelector("#textInput");

export async function requestBackend(mode) {
    let response;
    if (mode === 'image') {
        let file = imageInput.files[0];

        if (!file) {
            alert("Please select an image file.");
            return;
        }

        let formData = new FormData();
        formData.append("file", file);

        const BACKEND_URL = "http://127.0.0.1:2497/image-detect"; 
        response = await fetch(BACKEND_URL, {
            method: "POST",
            body: formData
        });
    } else if (mode === 'text') {
        let text = textInput.value.trim();

        if (!text) {
            alert("Please enter some text.");
            return;
        }

        const BACKEND_URL = "http://127.0.0.1:2497/text-detect";
        response = await fetch(BACKEND_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text })
        });
    } else {
        throw new Error("Invalid mode");
    }

    if (!response.ok) throw new Error("Error from backend");
    return await response.json();
}