 document.addEventListener("DOMContentLoaded", () => {
  const timerElement = document.getElementById("timer");
  const startTime = timerElement?.dataset.startTime || 0;
  
  if (startTime != 0) {
    startTimer(startTime);
  }

  const messagesContainer = document.getElementById("messages")
  if (messagesContainer){
    setTimeout(() => displayMessages(messagesContainer), 100);
    setTimeout(() => hideMessages(messagesContainer), 5000);
  }
  
  renderGraphs();
});

function startTimer(initialTime){
    console.log("starting timer from", initialTime)
    // should be inital time instead
    let startTime = new Date(initialTime);
    const timerEl = document.getElementById("timer");

    function updateTimer() {
    const now = Date.now();
    const elapsed = Math.floor((now - startTime) / 1000);
    const hours = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const minutes = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const seconds = String(elapsed % 60).padStart(2, '0');
    timerEl.textContent = `${hours}:${minutes}:${seconds}`;
    }

    setInterval(updateTimer, 1000);
}

function renderGraphs(){
    console.log("runing render_graphs function")
    renderBars()
    renderPieCharts()

}

function renderPieCharts() {
  const charts = document.querySelectorAll('.pie-chart');

  charts.forEach(container => {
    const percentage = parseInt(container.dataset.percentage) || 0;
    // Create SVG and its elements
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "21");
    svg.setAttribute("height", "21");
    svg.setAttribute("viewBox", "0 0 36 36");

    const radius = 14;
    const circumference = 2 * Math.PI * radius;
    const visible = (percentage / 100) * circumference;
    const invisible = circumference - visible;
    const padding = 4

    const bg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    bg.setAttribute("cx", radius + padding);
    bg.setAttribute("cy", radius + padding);
    bg.setAttribute("r", radius);
    bg.setAttribute("class", "bg")

    const fg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    fg.setAttribute("cx", radius + padding);
    fg.setAttribute("cy", radius + padding);
    fg.setAttribute("r", radius);
    fg.setAttribute("stroke-dasharray", `${visible} ${invisible}`);
    fg.setAttribute("class", "fg")

    svg.appendChild(bg);
    svg.appendChild(fg);

    // Clear and append
    container.innerHTML = "";
    container.appendChild(svg);
  });
}

function renderBars(){
    const scale = 1 / 1600;
    const bars = document.querySelectorAll('.duration-bar')
      bars.forEach(bar => {
        const duration = parseInt(bar.dataset.duration, 10) || 0;
        const duration_in_rem = String(duration*scale) + "rem"
        if (bar.classList.contains("vertical")){
            bar.style.height = duration_in_rem
        } else {
            bar.style.width = duration_in_rem
        }
    });
}

function displayMessages(container){
  container.style.right = "1rem";
}

function hideMessages(container){
  container.style.right = "-320px"
}