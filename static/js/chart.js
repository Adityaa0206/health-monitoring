// ⏳ Fetch the last 10 health records from Flask API
async function fetchHealthData() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        const timestamps = data.map(entry => entry.timestamp);
        const bpm = data.map(entry => entry.bpm);
        const spo2 = data.map(entry => entry.spo2);
        const temp = data.map(entry => entry.temperature);

        updateChart(timestamps, bpm, spo2, temp);
    } catch (error) {
        console.error("Failed to fetch health data:", error);
    }
}

let chartInstance = null;

// 📈 Create or update the Chart.js graph
function updateChart(labels, bpmData, spo2Data, tempData) {
    const ctx = document.getElementById('healthChart').getContext('2d');

    // Destroy previous chart instance if it exists
    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'BPM (Heart Rate)',
                    data: bpmData,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'SpO2 (%)',
                    data: spo2Data,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Temperature (°C)',
                    data: tempData,
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Measurement'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}

// 🔄 Refresh data every 5 seconds
setInterval(fetchHealthData, 5000);
fetchHealthData();
