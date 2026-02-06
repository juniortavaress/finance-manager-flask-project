import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { parseDateMaybe, quarterlyTickFormatter, tooltipCallbacks } from '../utils/chart-utils.js';

console.log("portfolioPerformanceChart.js loaded ✅");

document.addEventListener("DOMContentLoaded", () => {
  try {
    const historicData = loadJsonData('historic_by_broker'); 
    const ctx = getChartContext('investmentChartHome');
    const brokerSelector = document.getElementById('brokerSelector');
    let chart;

    // --- POPULATE THE SELECT ELEMENT ---
    const brokers = Object.keys(historicData);
    brokers.forEach(broker => {
      const option = document.createElement('option');
      option.value = broker;
      option.textContent = broker;
      brokerSelector.appendChild(option);
    });

    function parseCurrencyToNumber(str) {
      if (!str) return 0;
      return Number(str.replace("R$ ", "").replace("$ ", "").replace(/\./g, "").replace(",", "."));
    }
/**
     * Draws the performance chart based on selected broker
     */
    function drawInvestmentChart(selectedBroker = "all") {
      // 1. Determine which brokers to process
      const brokersToProcess = selectedBroker === "all" ? brokers : [selectedBroker];

      const isNomad = selectedBroker.toLowerCase() === "nomad";
      const currencyCode = isNomad ? 'USD' : 'BRL';
      const locale = isNomad ? 'en-US' : 'pt-BR';
      const yAxisTitle = isNomad ? "Value (USD)" : "Value (BRL)";

      // 2. Aggregate unique dates from all selected brokers
      const allDates = Array.from(
        new Set(brokersToProcess.flatMap(b => historicData[b].date))
      ).sort((a, b) => new Date(a) - new Date(b));

      const investedArray = [];
      const depositArray = [];
      const profitArray = [];

      // Object to keep track of the last seen value for each broker (for continuous lines)
      const lastValuePerBroker = {};
      brokersToProcess.forEach(b => {
        lastValuePerBroker[b] = { invested: 0, deposit: 0, profit: 0 };
      });

      // Loop through all dates to calculate daily totals
      for (const date of allDates) {
        let dailyTotalInvested = 0;
        let dailyTotalDeposit = 0;
        let dailyTotalProfit = 0;

        brokersToProcess.forEach(b => {
          const idx = historicData[b].date.indexOf(date);
          
          // If data exists for this specific date, update the last seen value
          if (idx !== -1) {
            lastValuePerBroker[b].invested = parseCurrencyToNumber(historicData[b].invested[idx]);
            lastValuePerBroker[b].deposit = parseCurrencyToNumber(historicData[b].contributions[idx]);
            lastValuePerBroker[b].profit = parseCurrencyToNumber(historicData[b].profit[idx]);
          }

          // Accumulate broker values into the daily total
          dailyTotalInvested += lastValuePerBroker[b].invested;
          dailyTotalDeposit += lastValuePerBroker[b].deposit;
          dailyTotalProfit += lastValuePerBroker[b].profit;
        });

        investedArray.push(dailyTotalInvested);
        depositArray.push(dailyTotalDeposit);
        profitArray.push(dailyTotalProfit);
      }

      // Destroy previous chart instance before re-drawing
      if (chart) chart.destroy();
      
      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: allDates,
          datasets: [
            {
              label: "Amount Deposited",
              data: depositArray,
              borderColor: "#8e44ad",
              backgroundColor: "rgba(142,68,173,0.1)",
              fill: true, 
              tension: 0.2, 
              pointRadius: 0,
              borderWidth: 2
            },
            {
              label: "Amount Invested",
              data: investedArray,
              borderColor: "#3498db",
              backgroundColor: "rgba(52,152,219,0.1)",
              fill: true,
              tension: 0.2,
              pointRadius: 0,
              borderWidth: 3
            },
            {
              label: "Total Profit",
              data: profitArray,
              borderColor: "#2ecc71",
              backgroundColor: "rgba(46,204,113,0.1)",
              fill: false,
              tension: 0.2,
              pointRadius: 0,
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false,
          },
          scales: {
            x: { 
              grid: { display: false }, 
              ticks: { callback: quarterlyTickFormatter(3) } 
            },
            y: { 
              beginAtZero: true, 
              title: { display: true, text: yAxisTitle } 
            }
          },
          plugins: {
            legend: { 
              position: "bottom", 
              labels: { usePointStyle: true, pointStyle: 'circle' } 
            },
            tooltip: { 
              callbacks: {
                label: function(context) {
                  let label = context.dataset.label || '';
                  if (label) label += ': ';
                  
                  if (context.parsed.y !== null) {
                    // 3. TOOLTIP DINÂMICO (R$ ou $)
                    label += new Intl.NumberFormat(locale, { 
                      style: 'currency', 
                      currency: currencyCode 
                    }).format(context.parsed.y);
                  }
                  return label;
                }} 
            }
          }
        }
      });
    }

    // --- EVENT LISTENER FOR BROKER FILTER ---
    brokerSelector.addEventListener('change', (e) => {
      drawInvestmentChart(e.target.value);
    });

    // Initial render with all data
    drawInvestmentChart("Nomad");

  } catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});