


document.addEventListener("DOMContentLoaded", () => {
    const script = document.getElementById("company-history");
    if (!script) return;

    const dataRaw = JSON.parse(script.textContent || "[]");
    if (!dataRaw.length) return;

    // Calcula price_total para cada ponto
    const data = dataRaw.map(d => ({
        ...d,
        price_total: d.invested * d.quantity
    }));

    const ctx = document.getElementById("investmentChartNu").getContext("2d");

    const labels = data.map(e => {
        const d = new Date(e.date);
        return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}`;
    });

    const metricsLabels = {
        current_invested: "Preço Atual",
        invested: "Preço Médio",
        price_total: "Preço Total",
        dividends: "Dividendos",
        profit: "Lucro",
        quantity: "Número de Ativos",
        profitability: "Rentabilidade"
    };

    const metricButtons = document.querySelectorAll(".metric-btn");

    // Inicializa com botões ativos
    let activeMetrics = Array.from(metricButtons)
        .filter(b => b.classList.contains("active"))
        .map(b => b.dataset.metric);

    function UserBankFetcherets(metricsArray) {
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

    const investmentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: UserBankFetcherets(activeMetrics)
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { title: { display: true, text: 'Data' } },
                y: { beginAtZero: true, title: { display: true, text: 'Valor' } }
            }
        }
    });

    function updateButtonStyles() {
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

    // Inicializa cores
    updateButtonStyles();

    // Eventos de clique
    metricButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const metric = btn.dataset.metric;
            btn.classList.toggle("active");

            activeMetrics = Array.from(metricButtons)
                .filter(b => b.classList.contains("active"))
                .map(b => b.dataset.metric);

            investmentChart.data.datasets = UserBankFetcherets(activeMetrics);
            investmentChart.update();

            updateButtonStyles();
        });
    });
});
