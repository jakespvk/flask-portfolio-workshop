const titleText = document.querySelector("#title-text")
const contentText = document.querySelector("#content-text")
const submitButton = document.querySelector("#submit-button")


function toggleSave(el) {
    submitButton.disabled = true
}

contentText.addEventListener('change', evt => {
    toggleSave(contentText);
})