console.log("✅ euro_cumulative_analysis.js loaded");

window.addEventListener('DOMContentLoaded', () => {

  const rawJson = document.getElementById('data-euro-incomes-expenses')?.textContent;
  if (!rawJson) return console.error("❌ JSON data not found");
  const data = JSON.parse(rawJson);

  const ctx = document.getElementById('chart-cumulative-euro')?.getContext('2d');
  if (!ctx) return console.error("❌ Canvas context not found");

  let cumulativeChart;

  function drawCumulativeChart(selectedYear = 'all') {
    const labels = [];
    const cumulative = [];

    if (selectedYear === 'all') {
      for (const year of Object.keys(data).sort()) {
        data[year].labels.forEach((month, i) => {
          labels.push(`${month} ${year}`);
          cumulative.push(data[year]['saldo acumulado'][i]);
        });
      }
    } 
    else {
      const yearData = data[selectedYear];
      if (!yearData) return;

      labels.push(...yearData.labels);
      cumulative.push(...yearData['saldo acumulado']);
    }

    if (cumulativeChart) cumulativeChart.destroy();

    const datasets = [
      {
        label: 'Accumulated Balance',
        data: cumulative,
        borderColor: 'green',
        backgroundColor: 'rgba(0,128,0,0.1)',
        fill: true,
        tension: 0.3
      }
    ];

    cumulativeChart = new Chart(ctx, {
      type: 'line',

      data: {
        labels,
        datasets
      },

      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {usePointStyle: true, boxWidth: 15, boxHeight: 5, padding: 20}
          },
          title: {display: false}
        },
        scales: {
          x: {grid: {drawOnChartArea: false, drawTicks: true}},
          y: {beginAtZero: true, title: {display: true, text: 'Amount (€)'}}
        }
      }
    });
  }

  // Init chart with all data
  drawCumulativeChart('all');

  // Handle year selection change
  document.getElementById('yearSelectCumulative')?.addEventListener('change', (e) => {
    drawCumulativeChart(e.target.value);
  });
});




