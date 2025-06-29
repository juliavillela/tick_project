window.addEventListener('DOMContentLoaded', () =>{
    console.log("runing tracker.js")
    const timerElement = document.getElementById("timer")
    const startTime = timerElement.dataset.startTime
    if (startTime != 0){
        startTimer(startTime)
    }
})

function startTimer(initialTime){
    console.log("starting timer from", initialTime)
    // should be inital time instead
    let startTime = new Date(initialTime);
    const timerEl = document.getElementById("timer");

    function updateTimer() {
    const now = Date.now();
    const elapsed = Math.floor((now - startTime) / 1000);
    const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const seconds = String(elapsed % 60).padStart(2, '0');
    timerEl.textContent = `${minutes}:${seconds}`;
    }

    setInterval(updateTimer, 1000);
}