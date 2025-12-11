console.log("real_graph.js foi carregado ✅");

document.addEventListener('DOMContentLoaded', () => {
  try{
    const rawJson = document.getElementById('data-finance-real-graphs').textContent;
    if (!rawJson) return console.error("❌ JSON data not found")
    const datas = JSON.parse(rawJson);

    const ctx = document.getElementById('div-chart-real').getContext('2d');
    if (!ctx) return console.error("❌ Canvas context not found")

    let realIncomeChart;

    const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    const somaArray = arr => arr.reduce((a, b) => a + b, 0);
    const monthName = monthStr => monthNames[parseInt(monthStr.split('/')[0], 10) - 1];

    // console.log(datas)
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
    
    function drawRealIncomeGraph(year_selection, view) {
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
              cumulative_balance.push(Math.max(m.cumulative, 0));
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
      if (realIncomeChart) realIncomeChart.destroy();

      realIncomeChart = new Chart(ctx, {
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

    drawRealIncomeGraph('2025', 'month');

    document.getElementById('viewSelect').addEventListener('change', e => {
      drawRealIncomeGraph(document.getElementById('yearSelect').value, e.target.value);
    });

    document.getElementById('yearSelect').addEventListener('change', e => {
      drawRealIncomeGraph(e.target.value, document.getElementById('viewSelect').value);
    });
  }

  catch (err) {
    console.error("Error loading or parsing the chart data:", err);
  }

});


//     // function somaArray(arr) {
//     //   return arr.reduce((a, b) => a + b, 0);
//     // }

//     const mesesOrdenados = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

//     function drawRealIncomeGraph(year_selected, view) {
//       let labels = [];
//       let entrada = [];
//       let saida = [];
//       let saldo = [];

//       if (year_selected === 'all') {
//         if (view === 'month') {
//           for (const year in data) {
//             mesesOrdenados.forEach(month => {
//               const dadosMes = data[year][month];
//               if (dadosMes) {
//                 labels.push(`${month} ${year}`);
//                 entrada.push(parseFloat(dadosMes['entrada'] || 0));
//                 saida.push(parseFloat(dadosMes['saida'] || 0));
//                 saldo.push(parseFloat(dadosMes['saldo'] || 0));
//               }
//             });
//           }
//         } 
        
//         else {
//           labels = Object.keys(data);
//           entrada = labels.map(year_selected => {
//             return Object.values(data[year_selected])
//               .map(m => m.entrada || 0)
//               .reduce((a, b) => a + b, 0).toFixed(2);
//           });
//           saida = labels.map(year_selected => {
//             return Object.values(data[year_selected])
//               .map(m => m.saida || 0)
//               .reduce((a, b) => a + b, 0).toFixed(2);
//           });
//           saldo = labels.map(year_selected => {
//             return Object.values(data[year_selected])
//               .map(m => m.saldo || 0)
//               .reduce((a, b) => a + b, 0).toFixed(2);
//           });
//         }
//       } else {
//         const dadosAno = data[year_selected];
//         if (!dadosAno) return;

//         if (view === 'month') {
//           mesesOrdenados.forEach(month => {
//             const dadosMes = dadosAno[month];
//             if (dadosMes) {
//               labels.push(month);
//               entrada.push(parseFloat(dadosMes['entrada'] || 0));
//               saida.push(parseFloat(dadosMes['saida'] || 0));
//               saldo.push(parseFloat(dadosMes['saldo'] || 0));
//             }
//           });
//         } else {
//           labels = [year_selected];
//           entrada = [Object.values(dadosAno).map(m => m.entrada || 0).reduce((a, b) => a + b, 0).toFixed(2)];
//           saida = [Object.values(dadosAno).map(m => m.saida || 0).reduce((a, b) => a + b, 0).toFixed(2)];
//           saldo = [Object.values(dadosAno).map(m => m.saldo || 0).reduce((a, b) => a + b, 0).toFixed(2)];
//         }
//       }

//       if (realIncomeChart) realIncomeChart.destroy();

//       realIncomeChart = new Chart(ctx, {
//         data: {
//           labels: labels, 
//           datasets: [
//             {
//               type: 'bar', 
//               label: 'Income',
//               data: entrada,
//               backgroundColor: 'rgba(75, 192, 192, 0.7)',
//               yAxisID: 'y'
//             },
//             {
//               type: 'bar', 
//               label: 'Expenses',
//               data: saida,
//               backgroundColor: 'rgba(255, 99, 132, 0.7)', 
//               yAxisID: 'y'
//             },
//             {
//               type: 'line',
//               label: 'Balance',
//               data: saldo,
//               borderColor: 'blue', 
//               backgroundColor: 'rgba(0,0,255,0.1)', 
//               fill: false, 
//               tension: 0.3, 
//               yAxisID: 'y'
//             }
//           ]
//         },
        
//         options: {
//           responsive: true, 
//           maintainAspectRatio: false, 
//           plugins: {
//             legend: {
//               display: true,
//               position: 'bottom', 
//               labels: {usePointStyle: true,  boxWidth: 15, boxHeight: 5, padding: 20}
//             },
//           },
//           scales: {
//             x: {
//               grid: {display: false}
//             },
//             y: {
//               beginAtZero: true, 
//               title: {display: true, text: chartAxis }, 
//             }
//           }
//         }
//       });
//     }


//     drawRealIncomeGraph('all', 'month');

//     document.getElementById('viewSelect').addEventListener('change', e => {
//       drawRealIncomeGraph(document.getElementById('yearSelect').value, e.target.value);
//     });

//     document.getElementById('yearSelect').addEventListener('change', e => {
//       drawRealIncomeGraph(e.target.value, document.getElementById('viewSelect').value);
//     });
//   }

//   catch (err) {
//     console.error("Error loading or parsing the chart data:", err);
//   }

// });
