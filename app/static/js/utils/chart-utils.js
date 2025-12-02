// chart-utils.js
console.log("chart-utils.js loaded ✅");

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


// graph cumulative
export function parseDateMaybe(d) {
  if (!d) return null;
  if (typeof d === "string") return new Date(d);
  if (d instanceof Date) return d;
  return new Date(d);
}

export function quarterlyTickFormatter(step) {
  return function(value, index) {
    if (index % step !== 0) return '';
    const date = new Date(this.getLabelForValue(value));
    const month = date.toLocaleString('pt-BR', { month: 'short' }).toLowerCase();
    const year = date.getFullYear().toString().slice(-2);
    return `${month}/${year}`;
  };
}

export const tooltipCallbacks = {
  title() {
    return ""; // remove a data do topo do tooltip
  },

  label(context) {
    const label = context.dataset.label;
    const value = context.parsed.y;

    if (label.includes("Lucro") || label.includes("Investido")) {
      // valores em reais
      return `${label}: R$ ${value.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    } else if (label.includes("Valor Aportado")) {
      return `R$ ${value.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    } else {
      // porcentagem
      return `${label}: ${value.toFixed(2)} %`;
    }
  }
};

// graph companies
export  function UserBankFetcherets(metricsArray, data, metricsLabels) {
        return metricsArray.map(metric => {
            const btn = document.querySelector(`.metric-btn[data-metric="${metric}"]`);
            const color = btn.dataset.color;
            return {
                label: metricsLabels[metric],
                data: data.map(d => d[metric]),
                borderColor: color,
                backgroundColor: color + "33",
                fill: true,
                tension: 0, // linhas retas
                pointRadius: 4,
                pointHoverRadius: 6
            };
        });
    }


export function updateButtonStyles(metricButtons) {
    metricButtons.forEach(b => {
        if (b.classList.contains("active")) {
            b.style.backgroundColor = b.dataset.color;
            b.style.color = "white";
            b.style.borderColor = b.dataset.color;
        } else {
            b.style.backgroundColor = "#f5f5f5";
            b.style.color = "black";
            b.style.borderColor = "#ccc";
        }
    });
}