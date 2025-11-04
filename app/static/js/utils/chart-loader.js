// chart-loader.js
console.log("chart-loader.js carregado ✅");

export function loadJsonData(elementId) {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id "${elementId}" not found.`);
    return null;
  }

  try {
    const data = JSON.parse(element.textContent.trim());
    return data;
  } catch (err) {
    console.error(`❌ Failed to parse JSON (${elementId}):`, err);
    return null;
  }
}


export function getChartContext(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`❌ Canvas com id "${canvasId}" não encontrado.`);
    return null;
  }
  return canvas.getContext('2d');
}

