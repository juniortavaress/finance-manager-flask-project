window.addEventListener('DOMContentLoaded', () => {
  const jsonData = document.getElementById('dados-json').textContent;
  const data = JSON.parse(jsonData);
  const ctx = document.getElementById('cumulativeChart').getContext('2d');

  let cumulativeChart;

  function drawCumulativeChart(selectedYear, viewMode) {
    let labels = [];
    let cumulative = [];

    if (selectedYear === 'all') {
      if (viewMode === 'mes') {
        // Para todos os anos, modo mensal: junta todos meses com o ano no label
        for (const year of Object.keys(data).sort()) {
          data[year].labels.forEach((month, i) => {
            labels.push(`${month} ${year}`);
            cumulative.push(data[year]['saldo acumulado'][i]);
          });
        }
      } else { // viewMode === 'ano'
        labels = Object.keys(data);
        cumulative = labels.map(year => {
          const arr = data[year]['saldo acumulado'];
          return arr[arr.length - 1];  // último saldo acumulado do ano
        });
      }
    } else {
      const currentData = data[selectedYear];
      if (!currentData) return;

      if (viewMode === 'mes') {
        labels = currentData.labels;
        cumulative = currentData['saldo acumulado'];
      } else { // viewMode === 'ano'
        labels = [selectedYear];
        const arr = currentData['saldo acumulado'];
        cumulative = [arr[arr.length - 1]];
      }
    }

    if (cumulativeChart) cumulativeChart.destroy();

    cumulativeChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Saldo Acumulado',
          data: cumulative,
          borderColor: 'green',
          backgroundColor: 'rgba(0,128,0,0.1)',
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          },
          title: {
            display: false,
            text: `Saldo Acumulado - ${selectedYear === 'all' ? 'Todos os Anos' : selectedYear} (${viewMode === 'mes' ? 'Mensal' : 'Anual'})`
          }
        },
        scales: {
          x: {
            grid: {
              drawOnChartArea: false
            }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '€'
            }
          }
        }
      }
    });
  }

  // Inicializa gráfico com todos os anos e modo mensal
  drawCumulativeChart('all', 'mes');

  // Atualiza gráfico quando o ano mudar
  document.getElementById('anoSelect02').addEventListener('change', e => {
    const selectedYear = e.target.value;
    const viewMode = document.getElementById('viewSelect').value;
    drawCumulativeChart(selectedYear, viewMode);
  });

  // Atualiza gráfico quando o modo mudar
  document.getElementById('viewSelect').addEventListener('change', e => {
    const viewMode = e.target.value;
    const selectedYear = document.getElementById('anoSelect02').value;
    drawCumulativeChart(selectedYear, viewMode);
  });
});
