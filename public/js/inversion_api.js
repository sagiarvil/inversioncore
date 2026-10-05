const INVERSION_API_BASE = "https://inversioncore-api.onrender.com";

async function sendToBackend(extractedText, customerId = "web_user") {
  if (!extractedText || extractedText.length < 10) {
    throw new Error("Metin çok kısa (min 10 karakter)");
  }

  const response = await fetch(`${INVERSION_API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: extractedText,
      customer_id: customerId
    })
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `API hatası: ${response.status}`);
  }

  return await response.json();
}

function displayNegativeFinding(result) {
  const termBox = document.getElementById("terminalBox") || document.getElementById("output");
  if (!termBox) {
    console.log("InversionCore Sonucu:", result);
    return;
  }

  const synthesis = result.synthesis?.synthesis
    || result.synthesis?.fallback_synthesis
    || JSON.stringify(result.synthesis, null, 2);

  const motorSummary = (result.motor_results || [])
    .map(r => `▸ ${r.motor || "?"}: ${r.negative_finding || "?"}`)
    .join("\n");

  const output = [
    "╔══════════════════════════════════════════════════╗",
    "║  INVERSIONCORE — NEGATİF BİLGİ RAPORU            ║",
    "╚══════════════════════════════════════════════════╝",
    "",
    `Problem Tipi: ${result.problem_type}`,
    "",
    "── MOTOR BULGULARI ──",
    motorSummary || "(bulgu yok)",
    "",
    "── SENTEZ ──",
    synthesis,
    "",
    `Cache: motor=${result.cache_stats?.motor} | sentez=${result.cache_stats?.synthesis}`,
    `Maliyet: $${(result.cost_summary?.total_cost_usd || 0).toFixed(6)}`,
    `Hit Oranı: %${result.cost_summary?.hit_rate || 0}`
  ].join("\n");

  termBox.innerText = output;
}

window.InversionAPI = { sendToBackend, displayNegativeFinding };
