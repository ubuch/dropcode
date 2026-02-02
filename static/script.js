// =====================
// UPLOAD
// =====================
const uploadForm = document.getElementById("upload-form");

if (uploadForm) {
    const uploadResultDiv = document.getElementById("result");
    const uploadButton = document.getElementById("upload-button");
    const fileInput = document.getElementById("upload");
    const uploadSection = document.getElementById("upload-section");
    const uploadResultSection = document.getElementById("upload-result");
    const codeText = document.getElementById("code-text");
    const qrImage = document.getElementById("qr-image");

    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        uploadButton.disabled = true;
        uploadButton.textContent = "Uploading";

        if (fileInput.files.length === 0) {
            uploadResultDiv.textContent = "Select a file";
            uploadButton.disabled = false;
            uploadButton.textContent = "Upload image";
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                uploadResultDiv.textContent =
                    errorData.error || "Error uploading file";
                return;
            }

            const data = await response.json();
            const code = data.code;
            const qrUrl = data.qr_url || `/qr/${code}`;

            uploadSection.style.display = "none";
            uploadResultSection.style.display = "block";

            codeText.textContent = code;
            qrImage.src = qrUrl;

            uploadResultDiv.textContent = "";
        } catch (error) {
            uploadResultDiv.textContent = "Network error. Please try again.";
        } finally {
            uploadButton.disables = false;
            uploadButton.textContent = "Upload image";
        }
    });
}

// =====================
// DOWNLOAD
// =====================
const downloadForm = document.getElementById("download-form");

if (downloadForm) {
    const resultDiv = document.getElementById("result");
    const previewSection = document.getElementById("preview-section");
    const previewImage = document.getElementById("preview-image");
    const downloadLink = document.getElementById("download-link");
    const downloadSection = document.getElementById("download-section");

    downloadForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const code = document.getElementById("code-input").value.trim();
        if (!code) return;

        resultDiv.textContent = "Fetching image...";

        try {
            const response = await fetch(`/download/${code}`);

            if (!response.ok) {
                resultDiv.textContent = "Invalid code";
                return;
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            const filename = response.headers.get("X-Filename") || "image.png";

            downloadSection.style.display = "none";
            previewSection.style.display = "block";

            previewImage.src = url;
            downloadLink.href = url;
            downloadLink.download = filename;

            resultDiv.textContent = "";
        } catch (err) {
            resultDiv.textContent = "Something went wrong";
        }
    });
}
