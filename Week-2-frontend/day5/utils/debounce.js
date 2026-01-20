/*import { debounce } from "./utils/debounce.js";

const handleSearch = debounce((e) => {
  const value = e.target.value.toLowerCase();
  const filtered = products.filter(p =>
    p.title.toLowerCase().includes(value)
  );
  renderProducts(filtered);
}, 400);

searchInput.addEventListener("input", handleSearch);*/

export default function debounce(fn, delay) {
let timer
return function (...args) {
clearTimeout(timer)
timer = setTimeout(() => fn.apply(this, args), delay)
}
}


