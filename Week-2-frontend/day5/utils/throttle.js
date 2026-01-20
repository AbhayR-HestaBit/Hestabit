/*const throttle = (fn, delay) => {
let lastCall = 0

return (...args) => {
const now = Date.now()

if (now - lastCall >= delay) {
lastCall = now
fn(...args)
}
}
}

export default throttle*/
export default function throttle(fn, limit) {
let inThrottle = false
return function (...args) {
if (!inThrottle) {
fn.apply(this, args)
inThrottle = true
setTimeout(() => inThrottle = false, limit)
}
}
}


