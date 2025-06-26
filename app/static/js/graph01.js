window.addEventListener('DOMContentLoaded', () => {
  // Espera o HTML estar completamente carregado e analisado (sem esperar imagens)
  // para só aí rodar o código JS, garantindo que todos os elementos existem.

  // Pega o texto JSON que está na tag <script type="application/json" id="dados-json">
  const jsonData = document.getElementById('dados-json').textContent;

  // Converte a string JSON para um objeto JavaScript
  const dados = JSON.parse(jsonData);

  // Pega o contexto 2D do canvas para desenhar o gráfico usando Chart.js
  const ctx = document.getElementById('myChart').getContext('2d');

  // Variável para guardar a instância atual do gráfico (para poder destruir antes de desenhar um novo)
  let myChart;

  // Função para somar todos os valores de um array (exemplo: somar todas entradas ou saídas)
  function somaArray(arr) {
    return arr.reduce((a, b) => a + b, 0);
  }

  // Função principal que desenha o gráfico, recebe:
  // - ano: string ('all' para todos, ou '2023', '2024' etc)
  // - view: string ('mes' para mensal, 'ano' para anual)
  function desenharGrafico(ano, view) {
    // Arrays para guardar os dados que serão usados no gráfico
    let labels = [];
    let entrada = [];
    let saida = [];

    // Se for "Todos os anos"
    if (ano === 'all') {
      if (view === 'mes') {
        // Visualização mensal para todos os anos: concatena todos os meses de todos os anos
        labels = [];
        entrada = [];
        saida = [];

        // Para cada ano nos dados
        for (const year in dados) {
          // Para cada mês do ano, adiciona ao array labels com mês + ano (ex: "Jan 2023")
          dados[year].labels.forEach((mes, i) => {
            labels.push(`${mes} ${year}`);
            entrada.push(dados[year].entrada[i]); // pega entrada do mês i
            saida.push(dados[year].saida[i]);     // pega saída do mês i
          });
        }
      } else {
        // Visualização anual para todos os anos: soma entrada e saída por ano, label = ano
        labels = Object.keys(dados); // pega todos os anos (ex: ['2023', '2024'])
        // para cada ano, soma as entradas e coloca no array entrada
        entrada = labels.map(ano => somaArray(dados[ano].entrada));
        // para cada ano, soma as saídas e coloca no array saida
        saida = labels.map(ano => somaArray(dados[ano].saida));
      }
    } else {
      // Para um ano específico selecionado
      const dadosAno = dados[ano];
      if (!dadosAno) return; // se não existir dados, sai da função

      if (view === 'mes') {
        // Visualização mensal: pega os meses, entrada e saída do ano específico
        labels = dadosAno.labels;
        entrada = dadosAno.entrada;
        saida = dadosAno.saida;
      } else {
        // Visualização anual: soma total de entrada e saída para aquele ano
        labels = [ano]; // só um label que é o ano
        entrada = [somaArray(dadosAno.entrada)];
        saida = [somaArray(dadosAno.saida)];
      }
    }

    // Calcula saldo = entrada - saída para cada ponto
    const saldo = entrada.map((v, i) => v - saida[i]);
    // console.log("Labels:", labels);
    // console.log("Entradas:", entrada);
    // console.log("Saídas:", saida);
    // console.log("Saldos:", saldo);

    // Se já existir um gráfico, destrói para recriar
    if (myChart) myChart.destroy();

    // Cria um novo gráfico com Chart.js
    myChart = new Chart(ctx, {
      data: {
        labels: labels, // labels do eixo X
        datasets: [
          {
            type: 'bar', // gráfico de barras para entrada
            label: 'Entrada',
            data: entrada,
            backgroundColor: 'rgba(75, 192, 192, 0.7)', // cor das barras
            yAxisID: 'y' // eixo Y principal
          },
          {
            type: 'bar', // gráfico de barras para saída
            label: 'Saída',
            data: saida,
            backgroundColor: 'rgba(255, 99, 132, 0.7)', // cor das barras
            yAxisID: 'y'
          },
          {
            type: 'line', // gráfico de linha para saldo
            label: 'Saldo',
            data: saldo,
            borderColor: 'blue', // cor da linha
            backgroundColor: 'rgba(0,0,255,0.1)', // preenchimento abaixo da linha (se fill: true)
            fill: false, // não preenche a área abaixo da linha
            tension: 0.3, // suaviza as curvas da linha
            yAxisID: 'y'
          }
        ]
      },
      
      options: {
        responsive: true, // gráfico redimensiona junto com o container
        maintainAspectRatio: false, // permite flexibilidade no tamanho do canvas
        plugins: {
          legend: {
            position: 'bottom', // legenda fica na parte de baixo
            labels: {
              usePointStyle: true, // legenda usa bolinhas ao invés de quadrados
              boxWidth: 15,
              boxHeight: 5,
              padding: 20 // espaçamento dentro da legenda
            }
          },
          title: {
            display: false, // título do gráfico não é exibido (se quiser, coloca true)
            text: `Fluxo de Caixa - ${ano === 'all' ? 'Todos os anos' : ano} (${view === 'mes' ? 'Mensal' : 'Anual'})`
          }
        },
        scales: {
          x: {
            grid: {
                drawBorder: false,    // remove a linha da borda do eixo X
                drawOnChartArea: false, // remove as linhas verticais no gráfico
                drawTicks: false       // remove os ticks (traços)
            }
          },
          y: {
            beginAtZero: true, // eixo Y começa do zero (não corta o gráfico)
            title: { display: true, text: 'Valor (€)' }, // título do eixo Y
            grid: {
                color: 'rgba(0,0,0,0.1)', // cor mais clara/transparente para as linhas horizontais
            }
          }
        }
      }
    });
  }

  // Chama a função para desenhar o gráfico inicialmente com todos os anos e visualização mensal
  desenharGrafico('all', 'mes');

  // Quando o usuário mudar o ano no select, atualiza o gráfico
  document.getElementById('anoSelect').addEventListener('change', e => {
    const ano = e.target.value; // valor do select ano
    const view = document.getElementById('viewSelect').value; // valor do select visualização
    desenharGrafico(ano, view);
  });

  // Quando o usuário mudar a visualização (mensal/anual), atualiza o gráfico
  document.getElementById('viewSelect').addEventListener('change', e => {
    const view = e.target.value; // valor do select visualização
    const ano = document.getElementById('anoSelect').value; // valor do select ano
    desenharGrafico(ano, view);
  });
});
