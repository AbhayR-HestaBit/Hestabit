const debounce = (fn, delay) => {
let timer
return (...args) => {
clearTimeout(timer)
timer = setTimeout(() => {
fn(...args)
}, delay)
}
}

/* practical execution */
const input = document.getElementById("search")

const handleSearch = (e) => {
console.log("Searching for:", e.target.value)
}

const debouncedSearch = debounce(handleSearch, 500)

if (input) {
input.addEventListener("input", debouncedSearch)
}
