let todos = []

const savedtodos= localStorage.getItem("todos")

if (savedtodos) {
try{
todos = JSON.parse(savedtodos)
} catch (error) {
todos = []
}
}

const todolist = document.getElementById("todo-list")

const rendertodos = () => {
todolist.innerHTML = ""

todos.forEach((todo, index) => {

const li = document.createElement("li")
li.textContent = todo

const deleteBtn = document.createElement("button")
deleteBtn.textContent = "X"

deleteBtn.addEventListener("click", () => {
deletetodo(index)
})

li.appendChild(deleteBtn)
todolist.appendChild(li)
})
}

const savetodos = () => {
localStorage.setItem("todos", JSON.stringify(todos))
}

const form = document.getElementById("todo-form")
const input = document.getElementById("todo-input")

form.addEventListener("submit", (e) => {
e.preventDefault()

const value = input.value.trim() 
if (!value) return

todos.push(value)
savetodos()
rendertodos()

input.value = ""
})

const deletetodo = (index) => {
todos.splice(index, 1)
savetodos()
rendertodos()
}

rendertodos()
