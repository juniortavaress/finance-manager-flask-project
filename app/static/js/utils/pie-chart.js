console.log("pie-chart.js carregado ✅");

// Constants
const somaArray = arr => arr.reduce((a, b) => a + b, 0);

const defaultColors = [
  '#4dc9f6', '#f78ca2', '#66bb6a', '#9575cd', '#ffca28',
  '#26a69a', '#90caf9', '#ba68c8', '#aed581', '#ffab91'
];


//  Exported Functions
export function getDatasetLabelsAndValues(dataObj) {
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  const total = somaArray(values);
  return { labels, values, total };
}

export function createPieChart(ctx, labels, title, values, total){
  return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          label: title,
          data: values,
          backgroundColor: defaultColors.slice(0, labels.length),
          borderWidth: 1,
          hoverOffset: 20,
          hoverBorderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: pieOptions(total),
      plugins: [createCenterTextPlugin(`R$ ${total.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 25, '#000')]
    });
}


// Auxiliary Functions
function pieOptions(total){
  return{
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    layout: { padding: 5 },
    plugins: {
      legend: {display: true, position: 'bottom', labels: {usePointStyle: true, pointStyle: 'circle', pointStyleWidth: 5, boxHeight: 5,  padding: 15}},
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.parsed ?? 0; 
            const percentage = ((value / total) * 100).toFixed(1);
            return `${percentage}%`;
          }
    },
  },
}}}

function createCenterTextPlugin(text, baseFontSize = 25, color = '#000') {
  return {
    id: 'centerText',
    beforeDraw(chart) {
      const { ctx, chartArea, config } = chart;
      const meta = chart.getDatasetMeta(0);
      const firstArc = meta?.data?.[0];
      if (!firstArc) return;

      const { x: centerX, y: centerY } = firstArc;
      const cutoutRadius = firstArc.innerRadius;

      let fontSize = baseFontSize;
      ctx.save();
      ctx.font = `${fontSize}px Arial`;
      let textWidth = ctx.measureText(text).width;

      const maxWidth = cutoutRadius * 1.8; 
      while (textWidth > maxWidth && fontSize > 10) {
        fontSize -= 1;
        ctx.font = `${fontSize}px Arial`;
        textWidth = ctx.measureText(text).width;
      }

      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, centerX, centerY);
      ctx.restore();
    }
  };
}

