console.log("graph-euro-price.js foi carregado ✅");

document.addEventListener("DOMContentLoaded", () => {
  
  try{
    const rawJson = document.getElementById('data-currency-graph').textContent;
    if (!rawJson) return console.error("❌ JSON data not found")
    const datas = JSON.parse(rawJson);

    const ctx = document.getElementById('chart-brl-eur').getContext('2d');
    if (!ctx) return console.error("❌ Canvas context not found")

    let currencyChart;

    function drawCurrencyChart() {
      let labels = datas.map(item => item.data); 
      let values = datas.map(item => item.valor_eur_brl); 

      if (currencyChart) currencyChart.destroy(); // destrói gráfico anterior se existir
      
      currencyChart = new Chart(ctx, {
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
          plugins: {
            legend: {display: false, position: 'top'},
            tooltip: {enabled: true}
          },
          scales: {
            x: {
              display: true,
              grid:{display: false},
              title: {display: true},
              ticks: {maxRotation: 0, minRotation: 0, autoSkip: false,
                callback: function(value, index) {
                  // Mostrar apenas a cada 4 pontos
                  if (index % 120 !== 0) return '';
                  const date = new Date(this.getLabelForValue(value));
                  const month = date.toLocaleString('pt-BR', { month: 'short' }).toLowerCase();
                  const year = date.getFullYear().toString().slice(-2);
                  return `${month}/${year}`;
                }
            }
            },
            y: {
              display: true,
              title: {display: true, text: 'Valor (BRL)'},
              beginAtZero: false
            }
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
