import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { parseDateMaybe, quarterlyTickFormatter, tooltipCallbacks } from '../utils/chart-utils.js';

console.log("portfolioPerformanceChart.js loaded ✅");
document.addEventListener("DOMContentLoaded", () => {
  try {
    const datas = loadJsonData('datas');
    const ctx = getChartContext('investmentChartHome');
    
    let chart;
    
    function drawInvestmentChart() {
      const allData = datas["all"];
      if (!allData || !allData.length) return console.error("❌ 'all' data not found");

      const sortedData = allData
        .map(e => ({ ...e, __date: parseDateMaybe(e.month || e.date) }))
        .filter(e => e.__date)
        .sort((a, b) => a.__date - b.__date);

      const labels = sortedData.map(e => e.__date);
      const investedArray = [];
      const profitArray = [];
      const profitabilityArray = [];
      const depositArray = [];

      let lastProfit = 0, lastProfitability = 0, lastInvested = 0; 
      let lastDeposit = 0;

      for (const e of sortedData) {
        lastProfit = Number(e.profit ?? lastProfit);
        lastProfitability = Number(e.profitability ?? lastProfitability) * 100;
        lastInvested = Number(e.current_invested ?? e.invested ?? lastInvested);
        lastDeposit = Number(e.deposit ?? lastDeposit);

        profitArray.push(lastProfit);
        profitabilityArray.push(lastProfitability);
        investedArray.push(lastInvested);
        
        depositArray.push(lastDeposit);
      }

      if (chart) chart.destroy();
      chart = new Chart(ctx, {
        type: "line",
        data: { 
          labels: labels,
          datasets: [
            {
              label: "Valor Aportado",
              data: depositArray,
              borderColor: "#8e44ad", // roxo diferente do azul do Investido
              backgroundColor: "rgba(142,68,173,0.2)",
              fill: false,
              tension: 0,
              borderWidth: 3,
              pointRadius: 0,
              yAxisID: 'y'
            },
            {
              label: "Valor Investido (R$)",
              data: investedArray,
              borderColor: "#3498db",
              backgroundColor: "rgba(52,152,219,0.2)",
              fill: false,
              tension: 0,
              borderWidth: 3,
              pointRadius: 0, // tamanho do ponto
              yAxisID: 'y'
            },
            {
              label: "Lucro Total (R$)",
              data: profitArray,
              borderColor: "#2ecc71",
              backgroundColor: "rgba(46,204,113,0.2)",
              fill: false,
              tension: 0,
              borderWidth: 3,
              pointRadius: 0,
              yAxisID: 'y'
            },
            {
              label: "Rentabilidade (%)",
              data: profitabilityArray,
              borderColor: "#f39c12",
              backgroundColor: "rgba(243,156,18,0.2)",
              fill: false,
              tension: 0,
              borderWidth: 3,
              pointRadius: 0,
              yAxisID: 'y1'
            }
          ]
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {grid: { drawOnChartArea: false }, ticks: {minRotation: 0, maxRotation: 0, callback: quarterlyTickFormatter(3)}},
            y: {beginAtZero: true, title: { display: true, text: "Valor (R$)" }},
            y1: {beginAtZero: true, position: 'right', title: { display: true, text: "Rentabilidade (%)" }, grid: { drawOnChartArea: false }}
          },
          plugins: {
            legend: {position: "bottom", align: "center", labels: { usePointStyle: true, boxWidth: 5, boxHeight: 5, padding: 15, pointStyle: 'circle' }},
            tooltip: {callbacks: tooltipCallbacks}
          },
        }
      });
    }

    drawInvestmentChart();
    // window.addEventListener("resize", () => {if (chart) chart.resize();});
  } 
  
  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
