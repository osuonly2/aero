let colorChart, historyChart, rangeChart;

// ===============================
// LIVE SENSOR DATA
// ===============================
async function updateLiveData() {
  try {
    const res = await fetch("/api/data");
    const data = await res.json();

    document.getElementById("temp").textContent =
      data.temperature !== null ? data.temperature.toFixed(1) : "--";

    document.getElementById("hum").textContent =
      data.humidity !== null ? data.humidity.toFixed(1) : "--";

    document.getElementById("ph").textContent =
      data.ph !== null ? data.ph.toFixed(2) : "--";

    document.getElementById("co").textContent =
      data.co_ppm !== null ? data.co_ppm.toFixed(1) : "--";

    document.getElementById("pump").textContent =
      data.pump_on ? "ON" : "OFF";

    updateColorChart(data.colors);
  } catch (e) {
    console.log("Live data error:", e);
  }
}

// ===============================
// COLOR CHART
// ===============================
function updateColorChart(colors) {
  const labels = Object.keys(colors);
  const values = Object.values(colors);

  if (!colorChart) {
    const ctx = document.getElementById("colorChart").getContext("2d");
    colorChart = new Chart(ctx, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [{
          data: values
        }]
      }
    });
  } else {
    colorChart.data.labels = labels;
    colorChart.data.datasets[0].data = values;
    colorChart.update();
  }
}

// ===============================
// HISTORY CHART
// ===============================
async function loadHistory() {
  const res = await fetch("/api/history");
  const data = await res.json();

  const labels = data.map(d => d.timestamp);
  const temps = data.map(d => d.temperature);
  const hums = data.map(d => d.humidity);

  const ctx = document.getElementById("historyChart").getContext("2d");

  historyChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: "Temperature", data: temps },
        { label: "Humidity", data: hums }
      ]
    }
  });
}

// ===============================
// DATE RANGE CHART
// ===============================
document.getElementById("rangeForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;

  const res = await fetch("/api/range", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end })
  });

  const data = await res.json();

  const labels = data.map(d => d.timestamp);
  const temps = data.map(d => d.temperature);

  const ctx = document.getElementById("rangeChart").getContext("2d");

  if (rangeChart) rangeChart.destroy();

  rangeChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: "Temperature", data: temps }
      ]
    }
  });
});

// ===============================
// AUTO UPDATE
// ===============================
setInterval(updateLiveData, 2000);

window.onload = () => {
  updateLiveData();
  loadHistory();
};
