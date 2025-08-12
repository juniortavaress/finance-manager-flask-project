console.log("euro_expenses_analysis.js foi carregado ✅");

window.addEventListener('DOMContentLoaded', () => {
  try {
    const rawJson = document.getElementById('data-euro-pie-chart').textContent;
    if (!rawJson) return console.error("❌ JSON data not found")
    const data = JSON.parse(rawJson)
    
    const ctx = document.getElementById('chart-euro-expenses-pie').getContext('2d');
    if (!ctx) return console.error("❌ Canvas context not found");

    let pieChart;

    function drawPieChart(selectedMonth) {
      const monthData = data[selectedMonth];

      if (!monthData) {
        console.warn('No data found for month: ${selectedMonth}');
        return;
      }

      const labels = Object.keys(monthData);
      const values = Object.values(monthData);
      const totalValue = values.reduce((acc, val) => acc + val, 0);

      if (pieChart) pieChart.destroy();

      const centerTextPlugin = {
        id: 'centerText',
        beforeDraw(chart) {
          const ctx = chart.ctx;
          const firstArc = chart.getDatasetMeta(0).data[0];

          if (!firstArc) return;  // Garante que o gráfico foi carregado

          const centerX = firstArc.x;
          const centerY = firstArc.y;

          const text = `€ ${totalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

          ctx.save();
          ctx.font = ' 25px Arial';
          ctx.fillStyle = '#000';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(text, centerX, centerY);
          ctx.restore();
        }
      };

      pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            label: 'Gastos por Categoria',
            data: values,
            backgroundColor: [
              '#4dc9f6', // azul claro (já usado)
              '#f78ca2', // rosa pastel (já usado)
              '#66bb6a', // verde suave
              '#9575cd', // lavanda moderna
              '#ffca28', // amarelo mostarda suave
              '#26a69a', // teal escuro
              '#90caf9', // azul bem claro
              '#ba68c8', // lilás
              '#aed581', // verde claro
              '#ffab91'  // laranja claro
            ],
            borderWidth: 1,
            hoverOffset: 20,
            hoverBorderWidth: 2
          }]
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          layout: {padding: 5},
          plugins: {
            legend: {
              display: true,
              position: 'bottom',
              labels: {boxWidth: 10, padding: 15}
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.parsed;
                  const dataArr = context.chart.data.datasets[0].data;
                  const total = dataArr.reduce((acc, val) => acc + val, 0);
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

    drawPieChart(document.getElementById('monthSelect').value);

    document.getElementById('monthSelect').addEventListener('change', e => {
      drawPieChart(e.target.value);
    });

  } 
  
  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});
