import { loadJsonData, getChartContext } from '../utils/chart-loader.js';
import { calculateYearTotals, getMonthlyData } from '../utils/chart-utils.js';

console.log("graph-bar-incomes-expenses.js loaded ✅");
document.addEventListener('DOMContentLoaded', () => {
  try{
    const datas = loadJsonData('data-incomes-expenses');
    const ctx = getChartContext('chart-incomes-expenses');
    let chart;
    
    function drawIncomeGraph(year_selection='all', view='month') {
      let labels = [], income = [], expense = [], cumulative = [];

      const years = year_selection === 'all' ? Object.keys(datas).sort() : [year_selection];
      years.forEach(year => {
        const yearData = datas[year];
        if (!yearData) return;

        if (view === 'month') {
          getMonthlyData(yearData).forEach(m => {
            labels.push(`${m.label} ${year}`);
            income.push(m.income);
            expense.push(m.expense);
            cumulative.push(m.cumulative);
          });
        } else {
          const totals = calculateYearTotals(yearData);
          labels.push(year);
          income.push(totals.totalIncome);
          expense.push(totals.totalExpense);
          cumulative.push(totals.cumulative);
        }
      });

      if (chart) chart.destroy();
      chart = new Chart(ctx, {
        data: {
          labels: labels, 
          datasets: [
            {
              type: 'bar', 
              label: 'Income',
              data: income,
              backgroundColor: 'rgba(75, 192, 192, 0.7)',
              yAxisID: 'y'
            },
            {
              type: 'bar', 
              label: 'Expenses',
              data: expense,
              backgroundColor: 'rgba(255, 99, 132, 0.7)', 
              yAxisID: 'y'
            },
            {
              type: 'line',
              label: 'Cumulative',
              data: cumulative,
              borderColor: 'blue', 
              backgroundColor: 'rgba(0,0,255,0.1)', 
              fill: false, 
              tension: 0.3, 
              yAxisID: 'y'
            }
          ]
        },
        
        options: {
          responsive: true, 
          maintainAspectRatio: false, 
          scales: {
            x: {grid: {display: false}}, 
            y: {beginAtZero: true, title: {display: true, text: chartAxis }}},
          plugins: {
            legend: {display: true, position: 'bottom', labels: {usePointStyle: true,  boxWidth: 15, boxHeight: 5, padding: 20}}
          },
        }
      });
    }

    drawIncomeGraph();
    function updateChartFromSelects() {
      const year = document.getElementById('yearSelect').value;  
      const view = document.getElementById('viewSelect').value;  
      drawIncomeGraph(year, view);  
    }
    document.getElementById('viewSelect').addEventListener('change', updateChartFromSelects);
    document.getElementById('yearSelect').addEventListener('change', updateChartFromSelects);
  }

  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }
});

  