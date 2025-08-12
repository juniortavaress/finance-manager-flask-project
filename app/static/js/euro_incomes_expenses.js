console.log("euro_incomes_expenses.js foi carregado ✅");

document.addEventListener('DOMContentLoaded', () => {

  try{
    const rawJson = document.getElementById('data-euro-incomes-expenses').textContent;
    if (!rawJson) return console.error("❌ JSON data not found")
    const datas = JSON.parse(rawJson);

    const ctx = document.getElementById('chart-euro-incomes-expenses').getContext('2d');
    if (!ctx) return console.error("❌ Canvas context not found")

    let incomeChart;

    function somaArray(arr) {
      return arr.reduce((a, b) => a + b, 0);
    }

    function drawIncomeGraph(year_selection, view) {
      let labels = [];
      let entrada = [];
      let saida = [];
      let saldo = [];

      // For all years
      if (year_selection === 'all') {
        if (view === 'month') {
          for (const year in datas) {
            datas[year].labels.forEach((mes, i) => {
              labels.push(`${mes} ${year}`);
              entrada.push(datas[year].entrada[i]); 
              saida.push(datas[year].saida[i]);     
              saldo.push(datas[year].saldo[i]);    
            });
          }
        } 
        
        else {
          labels = Object.keys(datas); // (ex: ['2023', '2024'])
          entrada = labels.map(year_selection => somaArray(datas[year_selection].entrada));
          saida = labels.map(year_selection => somaArray(datas[year_selection].saida));
          saldo = labels.map(year_selection => somaArray(datas[year_selection].saldo));
        }
      }

      // For a specific selected year
      else {
        const yearData = datas[year_selection];
        if (!yearData) return; 

        if (view === 'month') {
          labels = yearData.labels;
          entrada = yearData.entrada;
          saida = yearData.saida;
          saldo = yearData.saldo;
        } 
        
        else {
          labels = [year_selection]; 
          entrada = [somaArray(yearData.entrada)];
          saida = [somaArray(yearData.saida)];
          saldo = [somaArray(yearData.saldo)];
        }
      }

      if (incomeChart) incomeChart.destroy();

      incomeChart = new Chart(ctx, {
        data: {
          labels: labels, 
          datasets: [
            {
              type: 'bar', 
              label: 'Income',
              data: entrada,
              backgroundColor: 'rgba(75, 192, 192, 0.7)',
              yAxisID: 'y'
            },
            {
              type: 'bar', 
              label: 'Expenses',
              data: saida,
              backgroundColor: 'rgba(255, 99, 132, 0.7)', 
              yAxisID: 'y'
            },
            {
              type: 'line',
              label: 'Balance',
              data: saldo,
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

  