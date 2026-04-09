function loadGraph() {
    fetch("/api/response-times")
    .then(res => res.json())
    .then(data => {
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.values;
        chart.update();
    });
}

setInterval(loadGraph, 5000);