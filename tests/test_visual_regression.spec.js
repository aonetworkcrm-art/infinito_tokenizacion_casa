/**
 * 📸 DApp Familiar — Visual Regression Tests (Playwright)
 * ========================================================
 * Captura screenshots de todos los tabs y estados interactivos
 * para detectar cambios visuales no deseados.
 *
 * Los snapshots baseline se almacenan en tests/snapshots/<viewport>/
 *
 * Ejecutar:
 *   npx playwright test tests/test_visual_regression.spec.js           # comparar
 *   npx playwright test tests/test_visual_regression.spec.js --update-snapshots  # generar baseline
 *
 * Nota: Las animaciones (Matrix Rain, whale feed, contadores) se
 * congelan antes de cada captura usando page.evaluate().
 */

const { test, expect } = require("@playwright/test");
const path = require("path");

const DAPP_PATH = "file://" + path.resolve(__dirname, "../dapp/index.html");

// ═══════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════

/**
 * Congela todas las animaciones y contadores animados de la DApp
 * para obtener screenshots deterministas.
 *
 * Espera 1.5s antes de congelar para que animateDashboard() (60 frames ~1s)
 * termine naturalmente antes de sobrescribir los valores.
 */
async function freezeAnimations(page) {
  // Esperar a que la animación del dashboard complete (~1s para 60 frames a 60fps)
  await page.waitForTimeout(1500);

  await page.evaluate(() => {
    // 1. Detener requestAnimationFrame (Matrix Rain)
    const origRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = () => {};

    // 2. Detener intervalos (whale simulation cada 8s, clock cada 1s)
    const maxId = window.setInterval(() => {}, 0);
    for (let i = 1; i <= maxId; i++) {
      window.clearInterval(i);
    }

    // 3. Limpiar canvas de lluvia INFINITO
    const canvas = document.getElementById("infinitoCanvas");
    if (canvas) {
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    // 4. Congelar header stats
    document.getElementById("hdr-tokens").textContent = "1,000,000 TI";
    document.getElementById("hdr-whales").textContent = "99";
    document.getElementById("hdr-value").textContent = "$103,000";
    document.getElementById("dash-treasury").textContent = "$42,600.00";
    document.getElementById("dash-monthly").textContent = "$293,150.00";

    // 5. Fijar el clock en el header
    const sub = document.querySelector(".hdr-sub");
    if (sub) sub.textContent = "15 de junio de 2026, 14:30:00  |  Polygon Amoy Testnet";
  });
}

/**
 * Siembra el whale feed con datos estables para screenshots deterministas.
 * Se llama DESPUÉS de navegar al whale tab.
 */
async function seedWhaleFeed(page) {
  await page.evaluate(() => {
    // Sembrar mempool con datos fijos para screenshot determinista
    const stats = ["mp-total-val","mp-tx-count","mp-gas-avg","mp-whale-count"];
    const statVals = ["$3,840,690","18","87","6"];
    stats.forEach((id,i)=>{const el=document.getElementById(id);if(el)el.textContent=statVals[i]});

    document.getElementById("mp-block-info").textContent = "Bloque #8942031";
    document.getElementById("mp-age-info").textContent = "2s atr\u00e1s";

    // Sembrar Top 3 Whales
    const topList = document.getElementById("mp-top-list");
    if (topList) {
      const whales = [
        {rank:"\uD83E\uDD47",emoji:"\uD83D\uDC8E",type:"M\u00edtica",val:2150000,gas:142,from:"0x7ceB...1f9",to:"0x2791...174",age:"4s"},
        {rank:"\uD83E\uDD48",emoji:"\u2728",type:"Dorada",val:845000,gas:89,from:"0xc213...e8f",to:"0x0d50...F3a",age:"12s"},
        {rank:"\uD83E\uDD49",emoji:"",type:"Azul",val:192000,gas:56,from:"0x1a2b...4Cd",to:"0x7ceB...1f9",age:"23s"},
      ];
      topList.innerHTML = whales.map(w =>
        `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 14px;border-bottom:1px solid rgba(255,255,255,0.04);font-size:10px">` +
        `<span>${w.rank} ${w.emoji} <span style="color:var(--cy);font-weight:600">${w.type}</span></span>` +
        `<span style="font-weight:700;color:var(--rd)">$${w.val.toLocaleString()}</span>` +
        `<span style="font-family:monospace;color:var(--dim);font-size:8px">${w.gas} Gwei</span>` +
        `<span style="font-family:monospace;color:var(--dim);font-size:8px">${w.from} \u2192 ${w.to}</span>` +
        `<span style="color:var(--dim);font-size:8px">${w.age} atr\u00e1s</span></div>`
      ).join("");
    }

    // Sembrar alert box
    const alertTitle = document.getElementById("mp-alert-title");
    const alertDesc = document.getElementById("mp-alert-desc");
    const alertVal = document.getElementById("mp-alert-val");
    if (alertTitle) alertTitle.textContent = "\uD83D\uDC0B Ballena M\u00edtica Detectada";
    if (alertDesc) alertDesc.textContent = "Transacci\u00f3n de m\u00e1s de $1M USD detectada en el mempool. Preparando arbitraje Flash Loan...";
    if (alertVal) alertVal.textContent = "$2,150,000";

    // Sembrar filas del mempool
    const feed = document.getElementById("mp-feed");
    if (feed) {
      const head = feed.querySelector(".mp-row-head");
      feed.innerHTML = "";
      if (head) feed.appendChild(head);

      const txData = [
        {e:"\uD83D\uDC8E",t:"M\u00edtica",v:2150000,g:142,f:"0x7ceB...1f9",to:"0x2791...174",c:94},
        {e:"\u2728",t:"Dorada",v:845000,g:89,f:"0xc213...e8f",to:"0x0d50...F3a",c:87},
        {e:"",t:"Azul",v:192000,g:56,f:"0x1a2b...4Cd",to:"0x7ceB...1f9",c:76},
        {e:"\u2728",t:"Dorada",v:420690,g:128,f:"0x2791...174",to:"0xc213...e8f",c:92},
        {e:"",t:"Juvenil",v:23400,g:35,f:"0x0d50...F3a",to:"0x1a2b...4Cd",c:63},
        {e:"",t:"Azul",v:156000,g:72,f:"0x0d50...F3a",to:"0x7ceB...1f9",c:81},
        {e:"\u2728",t:"Dorada",v:385200,g:95,f:"0xc213...e8f",to:"0x2791...174",c:78},
        {e:"",t:"Juvenil",v:18700,g:42,f:"0x1a2b...4Cd",to:"0x0d50...F3a",c:55},
        {e:"",t:"Juvenil",v:31200,g:38,f:"0x2791...174",to:"0xc213...e8f",c:69},
        {e:"",t:"Azul",v:114500,g:61,f:"0x7ceB...1f9",to:"0x1a2b...4Cd",c:84},
      ];

      txData.forEach(tx => {
        const row = document.createElement("div");
        row.className = "mp-row";
        const valClass = tx.v >= 1000000 ? "mp-val-mega" : tx.v >= 250000 ? "mp-val-hi" : tx.v >= 50000 ? "mp-val-md" : "mp-val-lo";
        const confColor = tx.c > 85 ? "var(--grn)" : tx.c > 60 ? "var(--go)" : "var(--rd)";
        row.innerHTML =
          `<span>${tx.e}</span>` +
          `<span style="color:${confColor}">${tx.t}</span>` +
          `<span class="mp-val ${valClass}">$${tx.v.toLocaleString()}</span>` +
          `<span class="mp-gas">${tx.g} Gwei</span>` +
          `<span class="mp-addr">${tx.f}</span>` +
          `<span class="mp-addr">${tx.to}</span>` +
          `<span class="mp-conf" style="color:${confColor}">${tx.c}%</span>`;
        feed.appendChild(row);
      });

      // Ocultar scroll para altura fija
      feed.style.overflow = "hidden";
    }
  });
}

// ═══════════════════════════════════════════════════════════════════
// HOOKS — Solo para tests de escritorio (1440px)
// ═══════════════════════════════════════════════════════════════════

test.beforeEach(async ({ page }) => {
  await page.goto(DAPP_PATH);
  await page.waitForSelector("#tab-dashboard.act", { timeout: 5000 });
  await freezeAnimations(page);
});

// ═══════════════════════════════════════════════════════════════════
// 1. DASHBOARD — Vista General
// ═══════════════════════════════════════════════════════════════════

test.describe("Dashboard — Regresión Visual", () => {
  test("dashboard completo debe coincidir con el snapshot baseline", async ({ page }) => {
    await expect(page).toHaveScreenshot("dashboard-full.png", {
      fullPage: true,
    });
  });

  test("tarjetas de distribución 51/35/14 deben verse correctamente", async ({ page }) => {
    const distributionSection = page.locator("#tab-dashboard .cg").first();
    await expect(distributionSection).toHaveScreenshot("dashboard-distribution.png");
  });

  test("tabla de proyección de crecimiento debe coincidir", async ({ page }) => {
    const table = page.locator("#tab-dashboard table");
    await expect(table).toHaveScreenshot("dashboard-growth-table.png");
  });

  test("lista de miembros familiares debe coincidir", async ({ page }) => {
    const members = page.locator(".mt");
    await expect(members).toHaveScreenshot("dashboard-family-members.png");
  });

  test("header debe coincidir con el snapshot", async ({ page }) => {
    const header = page.locator(".hdr");
    await expect(header).toHaveScreenshot("dashboard-header.png");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 2. WHALE RADAR
// ═══════════════════════════════════════════════════════════════════

test.describe("Whale Radar — Regresión Visual", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-whales']").click();
    await page.waitForSelector("#tab-whales.act", { timeout: 5000 });
    await seedWhaleFeed(page);
  });

  test("whale radar completo debe coincidir con snapshot", async ({ page }) => {
    await expect(page).toHaveScreenshot("whale-full.png", { fullPage: true });
  });

  test("estadísticas del mempool deben verse correctamente", async ({ page }) => {
    const stats = page.locator(".mp-stats");
    await expect(stats).toHaveScreenshot("whale-mempool-stats.png");
  });

  test("feed de transacciones debe coincidir con snapshot", async ({ page }) => {
    const feed = page.locator("#mp-feed");
    await expect(feed).toHaveScreenshot("whale-mempool-feed.png");
  });

  test("oportunidades flash loan bloqueadas deben coincidir", async ({ page }) => {
    const flashOpps = page.locator("#flash-opps");
    await expect(flashOpps).toHaveScreenshot("whale-flash-loans-locked.png");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 3. STAKING — Content Locker
// ═══════════════════════════════════════════════════════════════════

test.describe("Staking — Regresión Visual", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-staking']").click();
    await page.waitForSelector("#tab-staking.act", { timeout: 5000 });
  });

  test("staking completo debe coincidir con snapshot (estado inicial)", async ({ page }) => {
    await expect(page).toHaveScreenshot("staking-full-initial.png", { fullPage: true });
  });

  test("tarjetas de staking deben verse en estado inicial 0", async ({ page }) => {
    const cards = page.locator("#tab-staking .cg").first();
    await expect(cards).toHaveScreenshot("staking-cards-initial.png");
  });

  test("sección de contenido premium debe coincidir", async ({ page }) => {
    const premiumSection = page.locator("#tab-staking .dl");
    await expect(premiumSection).toHaveScreenshot("staking-premium-content.png");
  });

  test.describe("después de stakeaer", () => {
    test.beforeEach(async ({ page }) => {
      await page.locator("#stake-amount").fill("10000");
      await page.locator('button[onclick="stakeTokens()"]').click();
      await page.waitForTimeout(500);
    });

    test("staking completo debe coincidir después de stakeaer 10,000 TI", async ({ page }) => {
      await expect(page).toHaveScreenshot("staking-full-after-stake.png", { fullPage: true });
    });

    test("notificación de staking exitoso debe verse", async ({ page }) => {
      const notif = page.locator("#notif");
      await expect(notif).toHaveScreenshot("staking-notification-success.png");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// 4. GOBERNANZA — Votación
// ═══════════════════════════════════════════════════════════════════

test.describe("Gobernanza — Regresión Visual", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-governance']").click();
    await page.waitForSelector("#tab-governance.act", { timeout: 5000 });
  });

  test("gobernanza completa debe coincidir con snapshot", async ({ page }) => {
    await expect(page).toHaveScreenshot("governance-full.png", { fullPage: true });
  });

  test("tarjetas de poder de voto deben verse correctamente", async ({ page }) => {
    const cards = page.locator("#tab-governance .cg").first();
    await expect(cards).toHaveScreenshot("governance-voting-power.png");
  });

  test("3 propuestas PIP deben coincidir con snapshot", async ({ page }) => {
    const proposals = page.locator("#proposals");
    await expect(proposals).toHaveScreenshot("governance-proposals.png");
  });

  test("prop1 (PIP-1) debe tener barra en 72%", async ({ page }) => {
    const prop1 = page.locator("#prop1");
    await expect(prop1).toHaveScreenshot("governance-prop1.png");
  });

  test.describe("después de votar", () => {
    test.beforeEach(async ({ page }) => {
      await page.locator("#prop2 button:has-text('Votar Sí')").click();
      await page.waitForTimeout(500);
    });

    test("prop2 debe actualizarse después de votar Sí", async ({ page }) => {
      const prop2 = page.locator("#prop2");
      await expect(prop2).toHaveScreenshot("governance-prop2-after-vote.png");
    });

    test("notificación de voto debe verse", async ({ page }) => {
      const notif = page.locator("#notif");
      await expect(notif).toHaveScreenshot("governance-notification-vote.png");
    });
  });

  test("historial de votaciones debe coincidir", async ({ page }) => {
    const history = page.locator("#tab-governance .cd").filter({ has: page.locator(".dr") }).last();
    await expect(history).toHaveScreenshot("governance-history.png");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 5. WALLET — Conexión
// ═══════════════════════════════════════════════════════════════════

test.describe("Wallet — Regresión Visual", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-wallet']").click();
    await page.waitForSelector("#tab-wallet.act", { timeout: 5000 });
  });

  test("wallet completa debe coincidir con snapshot (desconectada)", async ({ page }) => {
    await expect(page).toHaveScreenshot("wallet-full-disconnected.png", { fullPage: true });
  });

  test("botón conectar MetaMask debe verse en wallet desconectada", async ({ page }) => {
    const walletSection = page.locator("#tab-wallet .cd-lg");
    await expect(walletSection).toHaveScreenshot("wallet-disconnected-state.png");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 6. SISTEMA DE TABS — Integridad Visual
// ═══════════════════════════════════════════════════════════════════

test.describe("Sistema de Tabs — Regresión Visual", () => {
  const allTabs = [
    { id: "tab-whales", name: "whale-radar", selector: ".tab[data-tab='tab-whales']", after: async (page) => { await seedWhaleFeed(page); } },
    { id: "tab-staking", name: "content-locker", selector: ".tab[data-tab='tab-staking']" },
    { id: "tab-governance", name: "governance", selector: ".tab[data-tab='tab-governance']" },
    { id: "tab-wallet", name: "wallet", selector: ".tab[data-tab='tab-wallet']" },
    { id: "tab-shadow", name: "shadow-silo", selector: ".tab[data-tab='tab-shadow']" },
  ];

  for (const tab of allTabs) {
    test(`tab ${tab.name} debe mantener integridad visual al cambiar desde dashboard`, async ({ page }) => {
      await page.locator(tab.selector).click();
      await page.waitForSelector(`#${tab.id}.act`, { timeout: 5000 });
      if (tab.after) await tab.after(page);
      await expect(page).toHaveScreenshot(`tab-${tab.name}.png`, { fullPage: true });
    });
  }

  test("tabs deben verse correctamente en la barra de navegación", async ({ page }) => {
    const tabBar = page.locator(".tabs");
    await expect(tabBar).toHaveScreenshot("tab-bar.png");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 7. RESPONSIVE — Mobile/Tablet (usa test.use para viewport)
// ═══════════════════════════════════════════════════════════════════

test.describe("Responsive — Regresión Visual", () => {
  test.describe("Tablet (768px)", () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test("dashboard en tablet debe verse correctamente", async ({ page }) => {
      await page.goto(DAPP_PATH);
      await page.waitForSelector("#tab-dashboard.act", { timeout: 5000 });
      await freezeAnimations(page);
      await expect(page).toHaveScreenshot("responsive-tablet-dashboard.png", { fullPage: true });
    });
  });

  test.describe("Mobile (375px)", () => {
    test.use({ viewport: { width: 375, height: 812 } });

    test("dashboard en mobile debe verse correctamente", async ({ page }) => {
      await page.goto(DAPP_PATH);
      await page.waitForSelector("#tab-dashboard.act", { timeout: 5000 });
      await freezeAnimations(page);
      await expect(page).toHaveScreenshot("responsive-mobile-dashboard.png", { fullPage: true });
    });

    test("whale radar en mobile debe ser usable", async ({ page }) => {
      await page.goto(DAPP_PATH);
      await page.waitForSelector("#tab-dashboard.act", { timeout: 5000 });
      await freezeAnimations(page);
      await page.locator(".tab[data-tab='tab-whales']").click();
      await page.waitForSelector("#tab-whales.act", { timeout: 5000 });
      await seedWhaleFeed(page);
      await expect(page).toHaveScreenshot("responsive-mobile-whales.png", { fullPage: true });
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// 8. FLUJO COMPLETO — Regresión Visual Integrada
// ═══════════════════════════════════════════════════════════════════

test.describe("Flujo Completo — Regresión Visual", () => {
  test("flujo completo: stake → desbloquear → votar debe mantener integridad visual", async ({ page }) => {
    // 1. Dashboard inicial (ya cargado en beforeEach)
    await expect(page).toHaveScreenshot("flow-01-dashboard.png", { fullPage: true });

    // 2. Ir a staking y stakeaer
    await page.locator(".tab[data-tab='tab-staking']").click();
    await page.waitForSelector("#tab-staking.act", { timeout: 5000 });
    await expect(page).toHaveScreenshot("flow-02-staking-before.png", { fullPage: true });

    await page.locator("#stake-amount").fill("10000");
    await page.locator('button[onclick="stakeTokens()"]').click();
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot("flow-03-staking-after.png", { fullPage: true });

    // 3. Ver whale radar ahora desbloqueado
    await page.locator(".tab[data-tab='tab-whales']").click();
    await page.waitForSelector("#tab-whales.act", { timeout: 5000 });
    await seedWhaleFeed(page);
    await expect(page).toHaveScreenshot("flow-04-whales-unlocked.png", { fullPage: true });

    // 4. Votar en gobernanza
    await page.locator(".tab[data-tab='tab-governance']").click();
    await page.waitForSelector("#tab-governance.act", { timeout: 5000 });
    await expect(page).toHaveScreenshot("flow-05-governance-before.png", { fullPage: true });

    await page.locator("#prop2 button:has-text('Votar Sí')").click();
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot("flow-06-governance-after-vote.png", { fullPage: true });
  });
});
