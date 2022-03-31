// Cache DOM element
var bar = document.getElementById("title"),
pos = -525

// Animate title bar intro with js
const enterTitleBar = () => {
  pos+= 25
  bar.style.left = pos + 'px'
  if (pos < 0) window.requestAnimationFrame(enterTitleBar)
}

// Start
enterTitleBar()