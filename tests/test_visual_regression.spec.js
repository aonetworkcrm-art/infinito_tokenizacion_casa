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
    // Establecer valores fijos para el radar
    document.getElementById("whale-juvenil").textContent = "8";
    document.getElementById("whale-azul").textContent = "5";
    document.getElementById("whale-dorada").textContent = "3";
    document.getElementById("whale-mitica").textContent = "1";

    // Sembrar filas del feed
    const feed = document.getElementById("whale-feed");
    if (feed) {
      const rows = feed.querySelectorAll(".wf-row");
      const stableData = [
        { type: "Dorada", value: "420,690", addr: "0x7ceB...1f9", time: "14:32", conf: "96%" },
        { type: "Azul", value: "184,500", addr: "0x2791...174", time: "14:28", conf: "82%" },
        { type: "Juvenil", value: "23,400", addr: "0xc213...e8f", time: "14:15", conf: "71%" },
        { type: "Mitica", value: "2,150,000", addr: "0x0d50...F3a", time: "13:58", conf: "94%" },
        { type: "Dorada", value: "385,200", addr: "0x1a2b...4Cd", time: "13:42", conf: "78%" },
      ];
      rows.forEach((row, i) => {
        if (i < stableData.length) {
          const d = stableData[i];
          const confVal = parseInt(d.conf);
          const confColor = confVal > 85 ? "var(--grn)" : confVal > 60 ? "var(--go)" : "var(--rd)";
          const emojiMap = { Juvenil: "", Azul: "", Dorada: "✨", Mitica: "💎" };
          row.innerHTML =
            `<span>${emojiMap[d.type]} <span style="color:${confColor}">${d.type}</span></span>` +
            `<span style="color:var(--cy)">$${d.value}</span>` +
            `<span style="color:var(--dim)">${d.addr}</span>` +
            `<span style="color:var(--dim)">${d.time}</span>` +
            `<span style="color:${confColor}">${d.conf}</span>`;
        }
      });

      // Ocultar los 7 rows extras (solo mostramos 5 estables con datos fijos)
      // para que la altura del feed sea determinista entre ejecuciones
      for (let i = stableData.length; i < rows.length; i++) {
        rows[i].style.display = "none";
      }
      // Mantener maxHeight original (400px) para respetar el CSS real de la DApp
      // overflow:hidden evita que un scrollbar cambie el layout
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

  test("4 categorías de ballenas deben verse correctamente", async ({ page }) => {
    const categories = page.locator("#tab-whales .cg").first();
    await expect(categories).toHaveScreenshot("whale-categories.png");
  });

  test("feed de transacciones debe coincidir con snapshot", async ({ page }) => {
    const feed = page.locator("#whale-feed");
    await expect(feed).toHaveScreenshot("whale-feed.png");
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
