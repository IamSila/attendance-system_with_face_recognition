
const viewActions = document.getElementById("viewActions");
const actions = document.getElementById("edits");
const closeButton = document.getElementById("btn-close");




viewActions.addEventListener("click", () => {
    actions.classList.remove("hidden");
});

closeButton.addEventListener("click", () => {
    actions.classList.add("hidden");
});


