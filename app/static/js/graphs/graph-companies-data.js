import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { UserBankFetcherets, updateButtonStyles, parseDateMaybe } from '../utils/chart-utils.js';

console.log("graph-companies-data.js loaded ✅");
document.addEventListener("DOMContentLoaded", () => {
  try{
    const ctx = getChartContext('investmentChartNu');
    const dataRaw = loadJsonData('company-history');
    const datas = dataRaw.map(d => ({ ...d, price_total: d.invested * d.quantity }));
    
    let chart
    
    function drawCompaniesGraph(){
      const metricButtons = document.querySelectorAll(".metric-btn");  // Query all metric buttons from the DOM         
      const labels = datas.map(e => parseDateMaybe(e.date).toLocaleDateString('pt-BR'));
    
      const metricsLabels = {
        current_invested: "Preço Atual",
        invested: "Preço Médio",
        price_total: "Preço Total",
        dividends: "Dividendos",
        profit: "Lucro",
        quantity: "Número de Ativos",
        profitability: "Rentabilidade"
      };
    
      let activeMetrics = Array.from(metricButtons).filter(b => b.classList.contains("active")).map(b => b.dataset.metric);
    
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: UserBankFetcherets(activeMetrics, datas, metricsLabels)
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { title: { display: true, text: 'Data' } },
            y: { beginAtZero: true, title: { display: true, text: 'Valor' } }
          }
        }
      });
    
      updateButtonStyles(metricButtons); // Initialize button styles (active/inactive)
      metricButtons.forEach(btn => {
        btn.addEventListener("click", () => {
          btn.classList.toggle("active");
          activeMetrics = Array.from(metricButtons).filter(b => b.classList.contains("active")).map(b => b.dataset.metric);
          chart.data.datasets = UserBankFetcherets(activeMetrics, datas, metricsLabels);
          chart.update();
          updateButtonStyles(metricButtons);
        });
      });
    }

    drawCompaniesGraph()
  }

  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
