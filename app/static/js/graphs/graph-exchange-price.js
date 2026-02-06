import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { quarterlyTickFormatter } from '../utils/chart-utils.js';

console.log("graph-exchange-price.js loaded ✅");
document.addEventListener("DOMContentLoaded", () => {
  try{
    const datas = loadJsonData('data-currency-graph');
    const ctx = getChartContext('chart-brl-exchange');
    const coinCode = JSON.parse(document.getElementById('coin').textContent).toLowerCase();

    let chart;

    function drawCurrencyChart() {
      const valueKey = `valor_${coinCode}_brl`;

      let labels = datas.map(item => item.data); 
      let values = datas.map(item => item[valueKey]); 

      if (chart) chart.destroy(); 
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Price EUR/BRL',
            data: values,
            fill: false,
            borderColor: 'rgba(75, 192, 192, 1)',
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 6
          }]
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {display: true, grid:{display: false}, title: {display: true}, ticks: {maxRotation: 0, minRotation: 0, autoSkip: false, callback: quarterlyTickFormatter(120)}},
            y: {display: true, title: {display: true, text: 'Valor (BRL)'}, beginAtZero: false}
          },
          plugins: {
            legend: {display: false, position: 'top'},
            tooltip: {enabled: true}
          },
        }
      });
    }

    drawCurrencyChart();
    }

  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
