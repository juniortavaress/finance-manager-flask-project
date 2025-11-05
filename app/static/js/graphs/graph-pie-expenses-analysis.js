import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { createPieChart, getDatasetLabelsAndValues } from '../utils/pie-chart.js';
console.log("graph-pie-expenses-analysis.js foi carregado ✅");

document.addEventListener('DOMContentLoaded', () => {
  try {
    let chart;
    const datas = loadJsonData('data-euro-pie-chart');
    const ctx = getChartContext('chart-euro-expenses-pie');

    function drawPieChart(selectedMonth) {
      const monthData = datas[selectedMonth];
      if (!monthData) {console.warn(`No data found for month: ${selectedMonth}`); return;}

      const { labels, values, total } = getDatasetLabelsAndValues(monthData);

      if (chart) chart.destroy();
      chart = createPieChart(ctx, labels, 'Gasto', values, total)
    }

    drawPieChart(document.getElementById('monthSelect').value);
    document.getElementById('monthSelect').addEventListener('change', e => {drawPieChart(e.target.value);});
  } 
  
  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
