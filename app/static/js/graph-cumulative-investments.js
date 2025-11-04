console.log("portfolioPerformanceChart.js carregado ✅");

document.addEventListener("DOMContentLoaded", () => {
  try {
    const rawJson = document.getElementById("datas").textContent;
    if (!rawJson) return console.error("❌ JSON data not found");
    const data = JSON.parse(rawJson);

    const canvas = document.getElementById("investmentChartHome");
    if (!canvas) return console.error("❌ Canvas element not found");
    const ctx = canvas.getContext("2d");
    if (!ctx) return console.error("❌ Canvas context not found");

    let investmentChartInstance;

    function parseDateMaybe(d) {
      if (!d) return null;
      if (typeof d === "string") return new Date(d);
      if (d instanceof Date) return d;
      return new Date(d);
    }

    function drawInvestmentChart() {
      const allData = data["all"];
      if (!allData || !allData.length) return console.error("❌ 'all' data not found");

      const labels = [];
      const profitArray = [];
      const profitabilityArray = [];
      const investedArray = [];

      const sortedData = allData
        .map(e => ({ ...e, __date: parseDateMaybe(e.month || e.date) }))
        .sort((a, b) => a.__date - b.__date);

      let lastProfit = 0;
      let lastProfitability = 0;
      let lastInvested = 0;

      sortedData.forEach(e => {
        if (!e.__date) return;
        labels.push(e.__date);

        lastProfit = Number(e.profit ?? lastProfit);
        profitArray.push(lastProfit);

        lastProfitability = Number(e.profitability ?? lastProfitability) * 100; // em %
        profitabilityArray.push(lastProfitability);

        lastInvested = Number(e.current_invested ?? e.invested ?? lastInvested);
        investedArray.push(lastInvested);
      });

      const datasets = [
        {
          label: "Valor Investido (R$)",
          data: investedArray,
          borderColor: "#3498db",
          backgroundColor: "rgba(52,152,219,0.2)",
          fill: false,
          tension: 0.4,
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
          tension: 0.4,
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
          tension: 0.4,
          borderWidth: 3,
          pointRadius: 0,
          yAxisID: 'y1'
        }
      ];

      if (investmentChartInstance) investmentChartInstance.destroy();

      investmentChartInstance = new Chart(ctx, {
        type: "line",
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom", // horizontal
              align: "center",
              labels: { usePointStyle: true, boxWidth: 5, boxHeight: 5, padding: 15, pointStyle: 'circle' }
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  if (context.dataset.label.includes("Lucro") || context.dataset.label.includes("Investido")) {
                    return `${context.dataset.label}: R$ ${context.parsed.y.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                  } else {
                    return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} %`;
                  }
                }
              }
            }
          },
          scales: {
            x: {
              grid: { drawOnChartArea: false },
              ticks: {
                minRotation: 0, // horizontal
                maxRotation: 0, // horizontal
                callback: function(value, index) {
                  // Mostrar apenas de 3 em 3 meses
                  if (index % 3 !== 0) return '';
                  const date = this.getLabelForValue(value);
                  const d = new Date(date);
                  const month = (d.getMonth() + 1).toString().padStart(2, '0');
                  const year = d.getFullYear().toString().slice(-2);
                  return `${month}/${year}`;
                }
              }
            },
            y: { 
              beginAtZero: true,
              title: { display: true, text: "Valor (R$)" }
            },
            y1: {
              beginAtZero: true,
              position: 'right',
              title: { display: true, text: "Rentabilidade (%)" },
              grid: { drawOnChartArea: false }
            }
          }
        }
      });
    }

    drawInvestmentChart();

    window.addEventListener("resize", () => {
      if (investmentChartInstance) investmentChartInstance.resize();
    });

  } catch (err) {
    console.error("Erro ao carregar ou processar os dados do gráfico:", err);
  }
});
