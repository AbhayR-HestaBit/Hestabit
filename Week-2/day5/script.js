import { fetchProducts } from "./services/api.js";
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

init();
