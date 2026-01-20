/*import { fetchProducts } from "./services/api.js";
import { groupBy } from "./utils/groupBy.js";

import throttle from "./utils/throttle.js"

const onScroll = throttle(() => {
console.log("Scroll event fired", window.scrollY)
}, 500)

window.addEventListener("scroll", onScroll)

const payBtn = document.getElementById("pay-btn")

const handlePayment = throttle(() => {
console.log("Payment triggered")
}, 2000)

payBtn.addEventListener("click", handlePayment)
const grouped = groupBy(products, "category");
console.log(grouped);



const container = document.getElementById("products");

async function init() {
  const products = await fetchProducts();
  renderProducts(products);
}

function renderProducts(products) {
  container.innerHTML = "";

  products.forEach(p => {
    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
      <img src="${p.thumbnail}" />
      <h3>${p.title}</h3>
      <p>₹${p.price}</p>
      <p>${p.category}</p>
    `;

    container.appendChild(div);
  });
}

init();*/

import { fetchProducts } from "./services/api.js"
import { groupBy } from "./utils/groupBy.js"
import debounce from "./utils/debounce.js"
import throttle from "./utils/throttle.js"

let products = []
let currentView = []

const list = document.getElementById("product-list")
const searchInput = document.getElementById("search")
const categoryButtons = document.querySelectorAll("#categories button")
const sortHighLowBtn = document.getElementById("sort-high-low")
const sortLowHighBtn = document.getElementById("sort-low-high")

const renderProducts = (items) => {
list.innerHTML = ""
items.forEach(p => {
const li = document.createElement("li")

const img = document.createElement("img")
img.src = p.thumbnail

const title = document.createElement("h4")
title.textContent = p.title

const price = document.createElement("div")
price.className = "price"
price.textContent = `$ ${p.price}`

li.append(img, title, price)
list.appendChild(li)
})
}

const sortHighToLow = (items) => {
return [...items].sort((a, b) => b.price - a.price)
}

const sortLowToHigh = (items) => {
return [...items].sort((a, b) => a.price - b.price)
}

const init = async () => {
products = await fetchProducts()
currentView = [...products]
renderProducts(currentView)

const grouped = groupBy(products, "category")
console.log("GROUPED DATA", grouped)
}

categoryButtons.forEach(btn => {
btn.addEventListener("click", () => {
const cat = btn.dataset.category
currentView = cat === "all"
? [...products]
: products.filter(p => p.category === cat)
renderProducts(currentView)
})
})

searchInput.addEventListener("input", debounce((e) => {
const value = e.target.value.toLowerCase()
const result = currentView.filter(p =>
p.title.toLowerCase().includes(value)
)
renderProducts(result)
}, 300))

sortHighLowBtn.addEventListener("click", () => {
currentView = sortHighToLow(currentView)
renderProducts(currentView)
})

sortLowHighBtn.addEventListener("click", () => {
currentView = sortLowToHigh(currentView)
renderProducts(currentView)
})

window.addEventListener("scroll", throttle(() => {
console.log("scrolling...")
}, 1000))

init()
