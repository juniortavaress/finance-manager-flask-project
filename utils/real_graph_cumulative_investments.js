console.log("real_graph_cumulative_investments.js foi carregado ✅");

document.addEventListener('DOMContentLoaded', () => {

  try{
    const rawJson = document.getElementById('datas').textContent;
    if (!rawJson) return console.error("❌ JSON data not found")
    const data = JSON.parse(rawJson);

    const ctx = document.getElementById('chart-cumulative-investments').getContext('2d');
    if (!ctx) return console.error("❌ Canvas context not found")

    let cumulativeChart;

    const mesesOrdem = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    function drawCumulativeChart(selectedYear) {
      let labels = [];
      let saldoAcumulado = [];
      let aportesInvestimentos = [];
      let lucroInvestimentos = [];
      let totalInvestido = [];

      if (selectedYear === 'all') {
        const anosOrdenados = Object.keys(data).sort();

        anosOrdenados.forEach(year => {
          const mesesDoAno = data[year];

          mesesOrdem.forEach(month => {
            if (mesesDoAno[month]) {
              labels.push(`${month} ${year}`);
              saldoAcumulado.push(mesesDoAno[month]['saldo_acumulado'] ?? 0);
              aportesInvestimentos.push(mesesDoAno[month]['aportes investimentos'] ?? 0);
              lucroInvestimentos.push(mesesDoAno[month]['lucro investimentos'] ?? 0);
              totalInvestido.push(mesesDoAno[month]['total investido'] ?? 0);
            }
          });
        });
      } 
      
      else {
        const mesesDoAno = data[selectedYear];
        if (!mesesDoAno) return;

        mesesOrdem.forEach(month => {
          if (mesesDoAno[month]) {
            labels.push(month);
            saldoAcumulado.push(mesesDoAno[month]['saldo_acumulado'] ?? 0);
            aportesInvestimentos.push(mesesDoAno[month]['aportes investimentos'] ?? 0);
            lucroInvestimentos.push(mesesDoAno[month]['lucro investimentos'] ?? 0);
            totalInvestido.push(mesesDoAno[month]['total investido'] ?? 0);
          }
        });
      }

      if (cumulativeChart) cumulativeChart.destroy();

      const datasets = [
        {
          label: 'Saldo Acumulado',
          data: saldoAcumulado,
          borderColor: 'green',
          backgroundColor: 'rgba(0,128,0,0.1)',
          fill: false,
          tension: 0.3
        }
      ];

      if (aportesInvestimentos.some(v => v)) {
        datasets.push({
          label: 'Aportes Investimentos',
          data: aportesInvestimentos,
          borderColor: 'blue',
          fill: false,
          tension: 0.3
        });
      }

      if (lucroInvestimentos.some(v => v)) {
        datasets.push({
          label: 'Lucro Investimentos',
          data: lucroInvestimentos,
          borderColor: 'orange',
          fill: false,
          tension: 0.3
        });
      }

      if (totalInvestido.some(v => v)) {
        datasets.push({
          label: 'Total Investido',
          data: totalInvestido,
          borderColor: 'purple',
          fill: false,
          tension: 0.3
        });
      }

      cumulativeChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              position: 'bottom',
              labels: {usePointStyle: true, boxWidth: 15, boxHeight: 5, padding: 20} 
            },
            title: {
              display: false,
              text: `Saldo Acumulado - ${selectedYear === 'all' ? 'Todos os Anos' : selectedYear}`
            }
          },
          scales: {
            x: {grid: {drawOnChartArea: false }},
            y: {beginAtZero: true, title: { display: true, text: 'Valor (R$)' }}
          }
        }
      });
    }

    drawCumulativeChart('all');

    document.getElementById('yearSelectCumulative').addEventListener('change', e => {
      drawCumulativeChart(e.target.value);
    });
  }

  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }

});
