import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { parseDateMaybe, quarterlyTickFormatter, tooltipCallbacks } from '../utils/chart-utils.js';

console.log("portfolioPerformanceChart.js loaded ✅");

document.addEventListener("DOMContentLoaded", () => {
  try {
    // Pega o JSON injetado pelo template
    const historicData = loadJsonData('historic_by_broker'); // id="data-historic-by-broker" no HTML

    const ctx = getChartContext('investmentChartHome');
    let chart;

    function parseCurrencyToNumber(str) {
      if (!str) return 0;
      return Number(str.replace("R$ ", "").replace(".", "").replace(",", "."));
    }

    function drawInvestmentChart() {
      const brokers = Object.keys(historicData);
      if (!brokers.length) return console.error("❌ No broker data found");

      // Para simplificação, vamos juntar todas as datas únicas
      const allDates = Array.from(
        new Set(brokers.flatMap(b => historicData[b].date))
      ).sort((a, b) => new Date(a) - new Date(b));

      const investedArray = [];
      const depositArray = [];
      const profitArray = [];
      const profitabilityArray = [];

      let lastInvested = 0, lastDeposit = 0, lastProfit = 0, lastProfitability = 0;

      for (const date of allDates) {
        // Aqui você pode somar todos os brokers ou escolher um específico
        let invested = 0, deposit = 0, profit = 0;

        brokers.forEach(b => {
          const idx = historicData[b].date.indexOf(date);
          if (idx !== -1) {
            invested += parseCurrencyToNumber(historicData[b].invested[idx]);
            deposit += parseCurrencyToNumber(historicData[b].contributions[idx]);
            profit += parseCurrencyToNumber(historicData[b].profit[idx]);
          }
        });

        lastInvested = invested || lastInvested;
        lastDeposit = deposit || lastDeposit;
        lastProfit = profit || lastProfit;

        investedArray.push(lastInvested);
        depositArray.push(lastDeposit);
        profitArray.push(lastProfit);
        // rentabilidade opcional, se tiver
        profitabilityArray.push(lastInvested ? (lastProfit / lastInvested) * 100 : 0);
      }

      if (chart) chart.destroy();
      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: allDates,
          datasets: [
            {
              label: "Valor Aportado",
              data: depositArray,
              borderColor: "#8e44ad",
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
              pointRadius: 0,
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
            // {
            //   label: "Rentabilidade (%)",
            //   data: profitabilityArray,
            //   borderColor: "#f39c12",
            //   backgroundColor: "rgba(243,156,18,0.2)",
            //   fill: false,
            //   tension: 0,
            //   borderWidth: 3,
            //   pointRadius: 0,
            //   yAxisID: 'y1'
            // }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { drawOnChartArea: false }, ticks: { minRotation: 0, maxRotation: 0, callback: quarterlyTickFormatter(3) } },
            y: { beginAtZero: true, title: { display: true, text: "Valor (R$)" } },
            y1: { beginAtZero: true, position: 'right', title: { display: true, text: "Rentabilidade (%)" }, grid: { drawOnChartArea: false } }
          },
          plugins: {
            legend: { position: "bottom", align: "center", labels: { usePointStyle: true, boxWidth: 5, boxHeight: 5, padding: 15, pointStyle: 'circle' } },
            tooltip: { callbacks: tooltipCallbacks }
          }
        }
      });
    }

    drawInvestmentChart();

  } catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
