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
const form = document.getElementById("todo-form")
const input = document.getElementById("todo-input")

const rendertodos = () => {
todolist.innerHTML = ""

if (todos.length === 0){
todolist.innerHTML = "<li>No todos yet</li>"
return
}

todos.forEach((todo, index) => {

const li = document.createElement("li")
//li.textContent = todo

const span = document.createElement("span")
span.textContent = todo.text

const editBtn = document.createElement("button")
editBtn.textContent = "Edit"

const deleteBtn = document.createElement("button")
deleteBtn.textContent = "X"

editBtn.addEventListener("click", () => {
edittodo(index)
})

deleteBtn.addEventListener("click", () => {
deletetodo(index)
})

li.append(span, editBtn, deleteBtn)
todolist.appendChild(li)
})
}

const savetodos = () => {
localStorage.setItem("todos", JSON.stringify(todos))
}

form.addEventListener("submit", (e) => {
e.preventDefault()

const value = input.value.trim()
if (!value) return

todos.push({text:value})
savetodos()
rendertodos()

input.value = ""
})

const deletetodo = (index) => {
todos.splice(index,1)
savetodos()
rendertodos()
}

const edittodo = (index) => {
const newText = prompt("Edit todo", todos[index].text)
//const trimmed = newText.trim()
if (!newText) return
const trimmed = newText.trim()
if (!trimmed) return
todos[index].text = trimmed

//todos[index].text = newText.trim()
savetodos()
rendertodos()
}

rendertodos()

