console.log("euro_incomes_expenses.js foi carregado ✅");

document.addEventListener('DOMContentLoaded', () => {

  try{
    const rawJson = document.getElementById('data-euro-incomes-expenses').textContent;
    if (!rawJson) return console.error("❌ JSON data not found")
    const datas = JSON.parse(rawJson);

    const ctx = document.getElementById('chart-euro-incomes-expenses').getContext('2d');
    if (!ctx) return console.error("❌ Canvas context not found")

    let incomeChart;

    const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    const somaArray = arr => arr.reduce((a, b) => a + b, 0);
    const monthName = monthStr => monthNames[parseInt(monthStr.split('/')[0], 10) - 1];

    console.log(datas)
    function getMonthlyData(yearData) {
      return Object.keys(yearData).sort().map(m => {
        return {
          label: monthName(m),
          income: yearData[m].Income || 0,
          expense: yearData[m].Expense || 0,
          // balance: yearData[m].Balance || 0,
          cumulative: yearData[m].Cumulative_Balance || 0
        };
      });
    };

    function calculateYearTotals(yearData) {
      const totalIncome = somaArray(Object.values(yearData).map(v => v.Income || 0));
      const totalExpense = somaArray(Object.values(yearData).map(v => v.Expense || 0));
      const totalBalance = somaArray(Object.values(yearData).map(v => v.Balance || 0));
      const cumulative = Math.max(totalIncome - totalExpense, 0); // mantém >= 0
      return { totalIncome, totalExpense, totalBalance, cumulative };
    };
    
    function drawIncomeGraph(year_selection, view) {
      let labels = [];
      let income = [];
      let expense = [];
      let cumulative_balance = [];

      // For all years
      if (year_selection === 'all') {
        if (view === 'month') {
          for (const year in datas) {
            const yearData = datas[year];
            const monthlyData = getMonthlyData(yearData)

            monthlyData.forEach(m => {
              labels.push(`${m.label} ${year}`); 
              income.push(m.income);
              expense.push(m.expense);
              cumulative_balance.push(m.cumulative);
            });
          }
        } else {
            let runningTotal = 0;
            const years = Object.keys(datas).sort();

            years.forEach(year => {
              const yearData = datas[year];
              labels.push(year);

              const totals = calculateYearTotals(yearData);
              income.push(totals.totalIncome);
              expense.push(totals.totalExpense);

              runningTotal += totals.totalBalance; // acumula os anos
              cumulative_balance.push(runningTotal);
            });
        }}

      // For a specific selected year
      else { // year específico
        const yearData = datas[year_selection];
        if (!yearData) return;

        if (view === 'month') {
            const monthlyData = getMonthlyData(yearData);
            monthlyData.forEach(m => {
                labels.push(`${m.label} ${year_selection}`);
                income.push(m.income);
                expense.push(m.expense);
                cumulative_balance.push(m.cumulative);
            });
        } else { 
            const totals = calculateYearTotals(yearData);
            labels = [year_selection];
            income = [totals.totalIncome];
            expense = [totals.totalExpense];
            cumulative_balance = [totals.cumulative];
        }
      }

      // console.log(cumalutive_balance)
      if (incomeChart) incomeChart.destroy();

      incomeChart = new Chart(ctx, {
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
              data: cumulative_balance,
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
          plugins: {
            legend: {
              display: true,
              position: 'bottom', 
              labels: {usePointStyle: true,  boxWidth: 15, boxHeight: 5, padding: 20}
            },
          },
          scales: {
            x: {
              grid: {display: false}
            },
            y: {
              beginAtZero: true, 
              title: {display: true, text: chartAxis }, 
            }
          }
        }
      });
    }

    drawIncomeGraph('all', 'month');

    document.getElementById('viewSelect').addEventListener('change', e => {
      drawIncomeGraph(document.getElementById('yearSelect').value, e.target.value);
    });

    document.getElementById('yearSelect').addEventListener('change', e => {
      drawIncomeGraph(e.target.value, document.getElementById('viewSelect').value);
    });
  }

  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }

});

  