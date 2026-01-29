const form = document.getElementById("upload-form");
const resultDiv = document.getElementById("result");
const uploadButton = document.getElementById("upload-button");


form.addEventListener("submit", async (event) => {
    event.preventDefault(); // prevents the page from reloading
    
    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading";

    const fileInput = document.getElementById("upload");

    if (fileInput.files.length === 0) {
        resultDiv.textContent = "Select a file";
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload";
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
            resultDiv.textContent = errorData.error || "Error uploading file";
            return;
        }

        const data = await response.json();
        const code = data.code;
        
        document.getElementById("upload-section").style.display = "none";
        
        resultDiv.innerHTML = `
            <p>Your code is:</p>
            <h2>${code}</h2>
        `;
    } catch (error) {
        resultDiv.textContent = "Network error. Please try again.";
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload";
    }
});
