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
export function getDatasetLabelsAndValues(dataObj) {
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  const total = somaArray(values);
  return { labels, values, total };
}

export function createCenterTextPlugin(text, fontSize = 20, color = '#000') {
  return {
    id: 'centerText',
    beforeDraw(chart) {
      const { ctx, chartArea } = chart;
      const centerX = (chartArea.left + chartArea.right) / 2;
      const centerY = (chartArea.top + chartArea.bottom) / 2;

      ctx.save();
      ctx.font = `${fontSize}px Arial`;
      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, centerX, centerY);
      ctx.restore();
    }
  };
}

export const defaultColors = [
  '#4dc9f6', '#f78ca2', '#66bb6a', '#9575cd', '#ffca28',
  '#26a69a', '#90caf9', '#ba68c8', '#aed581', '#ffab91'
];

export function percentageTooltip(total) {
  return {
    label: function(context) {
      const label = context.label || '';
      const value = context.parsed;
      const percentage = ((value / total) * 100).toFixed(1);
      return `${label}: ${percentage}%`;
    }
  };
}