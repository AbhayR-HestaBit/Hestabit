const faqs = document.querySelectorAll(".faq")

faqs.forEach((faq) => {
const button = faq.querySelector(".question")

button.addEventListener("click", () => {
faq.classList.toggle("active")
})
})
