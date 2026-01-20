let count = 0

const countEl = document.getElementById("count")
const incrementBtn = document.getElementById("increment")
const decrementBtn = document.getElementById("decrement")
const resetBtn = document.getElementById("reset")

const updateUI = () => {
countEl.textContent = count
}

incrementBtn.addEventListener("click", () => {
count++
updateUI()
})

decrementBtn.addEventListener("click", () => {
count--
updateUI()
})

resetBtn.addEventListener("click", () => {
count = 0
updateUI()
})

document.addEventListener("keydown", (e) => {
if (e.key === "ArrowUp") {
count++
updateUI()
}

if (e.key === "ArrowDown") {
count--
updateUI()
}
})
