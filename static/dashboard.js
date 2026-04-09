function loadStats() {
    fetch("/api/stats")
    .then(res => res.json())
    .then(data => {
        document.getElementById("total").innerText = data.total;
        document.getElementById("healthy").innerText = data.healthy;
        document.getElementById("failed").innerText = data.failed;
        document.getElementById("avg").innerText = data.avg_time + "s";
    });
}

setInterval(loadStats, 5000);
loadStats();