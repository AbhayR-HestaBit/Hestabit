const faqData = [
{
question: "What is Render Tree?",
answer: "A combination of DOM tree and CSSOM Tree, without visually non appearing elements."
},
{
question: "What is Layout?",
answer: "The process of calculating position of nodes in Render tree."
},
{
question: "What is URI?",
answer: "Uniform Resource Identifier, Example: mailto:demouser@gmail.com"
}
]

const faqSection = document.querySelector('[aria-label="FAQ Section"]')

faqData.forEach(({ question, answer }) => {
const faq = document.createElement("div")
faq.className = "faq"

faq.innerHTML = `
<button class="question">${question}</button>
<div class="answer">
<p>${answer}</p>
</div>
`

faqSection.appendChild(faq)

const btn = faq.querySelector(".question")

btn.addEventListener("click", () => {
faq.classList.toggle("active")
})
})
