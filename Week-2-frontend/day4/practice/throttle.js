const throttle = (fn, limit) => {
let inThrottle = false

return (...args) => {
if (!inThrottle) {
fn(...args)
inThrottle = true
setTimeout(() => {
inThrottle = false
}, limit)
}
}
}

const handleScroll = () => {
console.log("Scroll event fired:", Date.now())
}

const throttledScroll = throttle(handleScroll, 1000)

window.addEventListener("scroll", throttledScroll)
