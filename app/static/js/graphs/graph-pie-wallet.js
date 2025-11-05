import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { createPieChart, getDatasetLabelsAndValues } from '../utils/pie-chart.js';

console.log("investmentChart.js loaded ✅");

document.addEventListener("DOMContentLoaded", () => {
  try {
    let chart;
    const ctx = getChartContext('wallet');
    const assetData = loadJsonData('assets');
    const { labels, values, total } = getDatasetLabelsAndValues(assetData);
    if (chart) chart.destroy();
    chart = createPieChart(ctx, labels, 'Valor', values, total)
  } 
  
  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
