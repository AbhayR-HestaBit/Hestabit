const productsEl = document.getElementById("products")

function renderSkeleton(count) {
productsEl.innerHTML = ""

for (let i = 0; i < count; i++) {
const card = document.createElement("div")
card.className = "card"

const img = document.createElement("div")
img.className = "skeleton image"

const title = document.createElement("div")
title.className = "skeleton title"

card.append(img, title)
productsEl.appendChild(card)
}
}

function fetchProducts() {
return fetch("https://fakestoreapi.com/products")
.then(res => res.json())
}

renderSkeleton(6)

fetchProducts().then(products => {

const cards = document.querySelectorAll(".card")

products.slice(0, cards.length).forEach((product, index) => {
const card = cards[index]
card.innerHTML = ""

const title = document.createElement("h4")
title.textContent = product.title

card.appendChild(title)
})

setTimeout(() => {
products.slice(0, cards.length).forEach((product, index) => {
const card = cards[index]
card.innerHTML = ""

const img = document.createElement("img")
img.src = product.image
img.style.width = "100px"

const title = document.createElement("h4")
title.textContent = product.title

card.append(img, title)
})
}, 500)

})
