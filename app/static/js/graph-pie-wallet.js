console.log("investmentChart.js carregado ✅");

document.addEventListener("DOMContentLoaded", () => {
  try {
    // Pegar os dados do HTML
    const assetsScript = document.getElementById("assets");
    const assetData = assetsScript ? JSON.parse(assetsScript.textContent) : null;

    const canvasWallet = document.getElementById("wallet");
    if (!canvasWallet || !assetData) return;

    const ctx = canvasWallet.getContext("2d");
    let pieChart;

    function drawWalletChart() {
      const labels = Object.keys(assetData);
      const values = Object.values(assetData);
      const totalValue = values.reduce((acc, val) => acc + val, 0);

      if (pieChart) pieChart.destroy();

      const centerTextPlugin = {
        id: 'centerText',
        beforeDraw(chart) {
          const ctx = chart.ctx;
          const firstArc = chart.getDatasetMeta(0).data[0];
          if (!firstArc) return;

          const centerX = firstArc.x;
          const centerY = firstArc.y;
          const text = `R$ ${totalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

          ctx.save();
          ctx.font = '25px Arial';
          ctx.fillStyle = '#000';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(text, centerX, centerY);
          ctx.restore();
        }
      };

      const backgroundColors = [
        '#4dc9f6', '#f78ca2', '#66bb6a', '#9575cd',
        '#ffca28', '#26a69a', '#90caf9', '#ba68c8',
        '#aed581', '#ffab91'
      ];

      pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            label: 'Distribuição da Carteira',
            data: values,
            backgroundColor: backgroundColors.slice(0, labels.length),
            borderWidth: 1,
            hoverOffset: 20,
            hoverBorderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          layout: { padding: 5 },
          plugins: {
            legend: {
              display: true,
              position: 'bottom',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    pointStyleWidth: 5, // diminui o tamanho da bolinha
                    boxHeight: 5, 
                    padding: 15
                }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.parsed;
                  const total = context.chart.data.datasets[0].data.reduce((a,b)=>a+b,0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${percentage}%`;
                }
              }
            }
          }
        },
        plugins: [centerTextPlugin]
      });
    }

    drawWalletChart();

  } catch (err) {
    console.error("Erro ao carregar o gráfico de pizza da carteira:", err);
  }
});
