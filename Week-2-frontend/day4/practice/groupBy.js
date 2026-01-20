const groupBy = (arr, key) => {
return arr.reduce((acc, item) => {
const group = item[key]
if (!acc[group]) {
acc[group] = []
}
acc[group].push(item)
return acc
}, {})
}

const users = [
{name: "Abhay", role: "admin"},
{name: "Rohit", role: "user"},
{name: "Aman", role: "admin"},
{name: "Neha", role: "user"}
]

const groupedUsers = groupBy(users, "role")
console.log(groupedUsers)
