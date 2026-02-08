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

        const files = fileInput.files;

        const formData = new FormData();
        for (const file of files) {
            formData.append("files", file);
        }

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
// =====================
// IMAGE MODAL
// =====================
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-image");
    const downloadBtn = document.getElementById("download-btn");

    const closeBtn = document.querySelector(".close");

    document.querySelectorAll(".thumb").forEach(img => {
        img.addEventListener("click", () => {
            modal.style.display = "flex";
            modalImg.src = img.dataset.full;
            downloadBtn.href = `/file/${img.src.split("/")[4]}/download`;
        });
    });

    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
        modalImg.src = "";
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
            modalImg.src = "";
        }
    });
});
