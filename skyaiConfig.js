// skyaiConfig.js

// 1. LÉPÉS: Cseréld le ezt a linket a TE végleges "Raw" JSON linkedre a Githubról!
// (Amíg nincs kész a repo, addig a lenti 'FALLBACK_CONFIG'-ot fogja használni a rendszer)
const REMOTE_CONFIG_URL = "https://raw.githubusercontent.com/SkyAI-Ecosystem/main-hub/main/skyai-master-config.json";

// 2. LÉPÉS: Ez a biztonsági tartalék. Ha a GitHub nem elérhető, ezt tölti be.
const FALLBACK_CONFIG = {
  tokens: {
    governance: {
      name: "SkyAI Governance",
      symbol: "SKY-GOV",
      address: "0x4B30d92243e88907751E016d33A23D3A1A560026", // 100M
    },
    utility: {
      name: "SkyAI Fuel",
      symbol: "SKY-UTIL",
      address: "0xcBbaDC40Cde0F12679a6b0b74fB732E02E60fa83", // 97M
    }
  },
  platforms: {
    empire: { url: "https://empire.skyai.io" },
    trading: { url: "https://trade.skyai.io" },
    terminal: { url: "https://terminal.skyai.io" }
  }
};

/**
 * Ez a fő függvény. Meghívja a központi JSON-t.
 * Ha sikerül, visszaadja a friss adatokat.
 * Ha nem, visszaadja a biztonsági mentést.
 */
export async function fetchSkyAIConfig() {
  try {
    console.log("🔄 SkyAI Config betöltése...");
    
    // 5 másodperces időkorlát (timeout), hogy ne fagyjon le az oldal, ha lassú a net
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(REMOTE_CONFIG_URL, { 
      signal: controller.signal,
      cache: "no-store" // Mindig a legfrissebb verziót kérje, ne cache-eljen
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP hiba! Státusz: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ SkyAI Config sikeresen betöltve a GitHubról.");
    return data;

  } catch (error) {
    console.warn("⚠️ Nem sikerült betölteni a távoli konfigot. Fallback használata.", error);
    return FALLBACK_CONFIG;
  }
}
