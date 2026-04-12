const imageInput = document.querySelector("#imageInput");

export async function requestBackend(mode) {
    if (mode === 'image') {
        let file = imageInput.files[0];

        if (!file) {
            alert("Please select an image file.");
            return;
        }

        let formData = new FormData();
        formData.append("file", file);

        const BACKEND_URL = "http://127.0.0.1:2497/image-detect"; 
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            body: formData
        });

            
        if (!response.ok) throw new Error("Error from backend");
        return await response.json();
    }
}