import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { getDatasetLabelsAndValues, createCenterTextPlugin, defaultColors, percentageTooltip } from '../utils/chart-utils.js';
console.log("graph-pie-expenses-analysis.js foi carregado ✅");

document.addEventListener('DOMContentLoaded', () => {
  try {
    const datas = loadJsonData('data-euro-pie-chart');
    const ctx = getChartContext('chart-euro-expenses-pie');
    let chart;

    function drawPieChart(selectedMonth) {
      const monthData = datas[selectedMonth];
      if (!monthData) {
        console.warn(`No data found for month: ${selectedMonth}`);
        return;
      }
      const { labels, values, total } = getDatasetLabelsAndValues(monthData);

      if (chart) chart.destroy();
      chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Gastos por Categoria',
              data: values,
              backgroundColor: defaultColors,
              borderWidth: 1,
              hoverOffset: 20,
              hoverBorderWidth: 2
            } 
          ]
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          layout: { padding: 5 },
          plugins: {
            legend: {display: true, position: 'bottom', 
            labels: { boxWidth: 10, padding: 15 }},
            tooltip: {callbacks: percentageTooltip(total)}
          }
        },

        plugins: [createCenterTextPlugin(total.toLocaleString('pt-BR', { minimumFractionDigits: 2 }))]
      });
    }

    drawPieChart(document.getElementById('monthSelect').value);
    document.getElementById('monthSelect').addEventListener('change', e => {drawPieChart(e.target.value);});

  } catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
