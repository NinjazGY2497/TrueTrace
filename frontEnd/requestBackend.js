const BASE_URL = "https://hackathoncrewraag.pythonanywhere.com";
const imageInput = document.querySelector("#imageInput");
const textInput = document.querySelector("#textInput");

async function postJson(path, payload) {
    const response = await fetch(`${BASE_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const error = await response.json().catch(() => null);
        throw new Error(error?.error || "Backend request failed");
    }
    return response.json();
}

async function postForm(path, formData) {
    const response = await fetch(`${BASE_URL}${path}`, {
        method: "POST",
        body: formData,
    });
    if (!response.ok) {
        const error = await response.json().catch(() => null);
        throw new Error(error?.error || "Backend request failed");
    }
    return response.json();
}

export async function requestBackend(mode) {
    if (mode === "image") {
        const file = imageInput.files[0];
        if (!file) {
            alert("Please select an image file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        return postForm("/image-detect", formData);
    }

    if (mode === "text") {
        const text = textInput.value.trim();
        if (!text) {
            alert("Please enter some text.");
            return;
        }
        return postJson("/text-detect", { text });
    }

    throw new Error("Invalid mode");
}