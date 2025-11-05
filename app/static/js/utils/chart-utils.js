// chart-utils.js
console.log("chart-utils.js carregado ✅");

const somaArray = arr => arr.reduce((a, b) => a + b, 0);

export function getMonthlyData(yearData) {
  const formatter = new Intl.DateTimeFormat('en', { month: 'short' }); // Jan, Feb, ...
  
  return Object.keys(yearData).sort().map(m => {
    const monthNumber = parseInt(m.split('/')[0], 10); // 01, 02, 03 → 1, 2, 3
    const date = new Date(2020, monthNumber - 1); // só para pegar o nome do mês
    return {
      label: formatter.format(date), // Jan, Feb, Mar ...
      income: yearData[m].Income || 0,
      expense: yearData[m].Expense || 0,
      cumulative: yearData[m].Cumulative_Balance || 0
    };
  });
}

export function calculateYearTotals(yearData) {
  const totalIncome = somaArray(Object.values(yearData).map(v => v.Income || 0));
  const totalExpense = somaArray(Object.values(yearData).map(v => v.Expense || 0));
  const totalBalance = somaArray(Object.values(yearData).map(v => v.Balance || 0));
  const cumulative = Math.max(totalIncome - totalExpense, 0); // mantém >= 0
  return { totalIncome, totalExpense, totalBalance, cumulative };
}

export function updateChartFromSelects() {
  const year = document.getElementById('yearSelect').value;  
  const view = document.getElementById('viewSelect').value;  
  drawIncomeGraph(year, view);  
}



// PIE
export const defaultColors = [
  '#4dc9f6', '#f78ca2', '#66bb6a', '#9575cd', '#ffca28',
  '#26a69a', '#90caf9', '#ba68c8', '#aed581', '#ffab91'
];

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

export function getDatasetLabelsAndValues(dataObj) {
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  const total = somaArray(values);
  return { labels, values, total };
}

export function pieOptions(total){
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

export function createCenterTextPlugin(text, baseFontSize = 25, color = '#000') {
  return {
    id: 'centerText',
    beforeDraw(chart) {
      const { ctx, chartArea, config } = chart;
      const meta = chart.getDatasetMeta(0);
      const firstArc = meta?.data?.[0];
      if (!firstArc) return;

      const { x: centerX, y: centerY } = firstArc;

      // pega o raio total e o cutout (o buraco no meio)
      const chartRadius = firstArc.outerRadius;
      const cutoutRadius = firstArc.innerRadius;
      const availableRadius = (chartRadius - cutoutRadius) / 2 + cutoutRadius * 0.9; // pequena margem

      // começa com um tamanho base de fonte
      let fontSize = baseFontSize;
      ctx.save();
      ctx.font = `${fontSize}px Arial`;
      let textWidth = ctx.measureText(text).width;

      // reduz a fonte enquanto o texto for maior que o diâmetro do buraco
      const maxWidth = cutoutRadius * 1.8; // quanto do centro o texto pode ocupar
      while (textWidth > maxWidth && fontSize > 10) {
        fontSize -= 1;
        ctx.font = `${fontSize}px Arial`;
        textWidth = ctx.measureText(text).width;
      }

      // desenha o texto no centro
      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, centerX, centerY);
      ctx.restore();
    }
  };
}










// graph cumulative
export function parseDateMaybe(d) {
  if (!d) return null;
  if (typeof d === "string") return new Date(d);
  if (d instanceof Date) return d;
  return new Date(d);
}

export function quarterlyTickFormatter(value, index) {
  if (index % 3 !== 0) return '';
  const date = this.getLabelForValue(value);
  const d = new Date(date);
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const year = d.getFullYear().toString().slice(-2);
  return `${month}/${year}`;
}

export const tooltipCallbacks = {
  label(context) {
    const label = context.dataset.label;
    const value = context.parsed.y;

    if (label.includes("Lucro") || label.includes("Investido")) {
      // valores em reais
      return `${label}: R$ ${value.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    } else {
      // porcentagem
      return `${label}: ${value.toFixed(2)} %`;
    }
  }
};