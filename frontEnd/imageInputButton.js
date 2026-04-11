document.getElementById("imageInput").addEventListener("change", function() {
    const file = this.files[0];
    const preview = document.getElementById("imagePreview");
    const analyzeBtn = document.getElementById("analyzeImageBtn");

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = '<br><img src="' + e.target.result + '" width="400">';
            analyzeBtn.style.display = "inline-block";
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = "";
        analyzeBtn.style.display = "none";
    }
});