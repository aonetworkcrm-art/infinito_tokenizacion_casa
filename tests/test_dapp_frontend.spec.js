/**
 * 🧪 DApp Familiar — Tests de Frontend (Playwright)
 *
 * Pruebas end-to-end sobre el archivo HTML directamente.
 * Cubre: tabs, staking, votación, notificaciones, animaciones.
 *
 * Ejecutar:
 *   npx playwright test tests/test_dapp_frontend.spec.js
 */

const { test, expect } = require("@playwright/test");
const path = require("path");

const DAPP_PATH = "file://" + path.resolve(__dirname, "../dapp/index.html");

// ═══════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════

/** Click the exact "🔒 Stakear" button (not "Unstakear"). */
async function clickStake(page) {
  await page.locator('button[onclick="stakeTokens()"]').click();
}

/** Click the exact "🔓 Unstakear" button. */
async function clickUnstake(page) {
  await page.locator('button[onclick="unstakeTokens()"]').click();
}

/** Click a specific vote button inside a proposal. */
async function clickVote(page, propId, isYes) {
  const label = isYes ? "Votar Sí" : "Votar No";
  await page.locator(`#${propId} button:has-text("${label}")`).click();
}

// ═══════════════════════════════════════════════════════════════════
// HOOKS
// ═══════════════════════════════════════════════════════════════════

test.beforeEach(async ({ page }) => {
  await page.goto(DAPP_PATH, { waitUntil: "networkidle" });
  await page.waitForSelector("#tab-dashboard.act", { timeout: 10000 });
});

// ═══════════════════════════════════════════════════════════════════
// 1. HEADER & INITIAL STATE
// ═══════════════════════════════════════════════════════════════════

test.describe("Header y Estado Inicial", () => {
  test("debe mostrar el título del proyecto", async ({ page }) => {
    await expect(page.locator(".hdr-title")).toContainText("Centro de Mando Familiar");
  });

  test("debe mostrar las 3 stats del header", async ({ page }) => {
    await expect(page.locator("#hdr-tokens")).toBeVisible();
    await expect(page.locator("#hdr-whales")).toBeVisible();
    await expect(page.locator("#hdr-value")).toBeVisible();
  });

  test("debe mostrar el badge de sistema activo en el header", async ({ page }) => {
    const badge = page.locator(".hdr-stats .bg-gr");
    await expect(badge).toContainText("Sistema Activo");
  });

  test("debe tener 6 tabs con labels correctos", async ({ page }) => {
    const tabs = page.locator(".tab");
    await expect(tabs).toHaveCount(6);
    await expect(tabs.nth(0)).toContainText("DASHBOARD");
    await expect(tabs.nth(1)).toContainText("WHALE RADAR");
    await expect(tabs.nth(2)).toContainText("CONTENT LOCKER");
    await expect(tabs.nth(3)).toContainText("GOBERNANZA");
    await expect(tabs.nth(4)).toContainText("WALLET");
    await expect(tabs.nth(5)).toContainText("SHADOW SILO");
  });

  test("debe mostrar el footer con créditos", async ({ page }) => {
    const footer = page.locator(".ft");
    await expect(footer).toContainText("PROYECTO INFINITO");
    await expect(footer).toContainText("Buffy");
  });

  test("debe tener canvas con letras de INFINITO cayendo", async ({ page }) => {
    await expect(page.locator("#infinitoCanvas")).toBeVisible();
    // Verificar que el canvas existe y tiene dimensiones
    const width = await page.locator("#infinitoCanvas").getAttribute("width");
    expect(parseInt(width)).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════
// 2. TAB SYSTEM
// ═══════════════════════════════════════════════════════════════════

test.describe("Sistema de Tabs", () => {
  test("dashboard debe estar activo por defecto", async ({ page }) => {
    await expect(page.locator("#tab-dashboard")).toHaveClass(/act/);
    await expect(page.locator(".tab[data-tab='tab-dashboard']")).toHaveClass(/act/);
  });

  test("click en Whale Radar debe activar su tab", async ({ page }) => {
    await page.locator(".tab[data-tab='tab-whales']").click();
    await expect(page.locator("#tab-whales")).toHaveClass(/act/);
    await expect(page.locator("#tab-dashboard")).not.toHaveClass(/act/);
    await expect(page.locator("#mp-total-val")).toBeVisible();
  });

  test("click en Content Locker debe activar staking", async ({ page }) => {
    await page.locator(".tab[data-tab='tab-staking']").click();
    await expect(page.locator("#tab-staking")).toHaveClass(/act/);
    await expect(page.locator("#stake-balance")).toBeVisible();
    await expect(page.locator("#stake-amount")).toBeVisible();
  });

  test("click en Gobernanza debe activar propuestas", async ({ page }) => {
    await page.locator(".tab[data-tab='tab-governance']").click();
    await expect(page.locator("#tab-governance")).toHaveClass(/act/);
    await expect(page.locator("#prop1")).toBeVisible();
    await expect(page.locator("#prop2")).toBeVisible();
    await expect(page.locator("#prop3")).toBeVisible();
  });

  test("click en Wallet debe mostrar boton conectar", async ({ page }) => {
    await page.locator(".tab[data-tab='tab-wallet']").click();
    await expect(page.locator("#tab-wallet")).toHaveClass(/act/);
    await expect(page.locator("#wallet-btn")).toContainText("Conectar MetaMask");
    await expect(page.locator("#wallet-status")).toContainText("No conectado");
  });

  test("debe permitir navegar entre todos los tabs", async ({ page }) => {
    for (const tabId of ["tab-dashboard", "tab-whales", "tab-staking", "tab-governance", "tab-wallet", "tab-shadow"]) {
      await page.locator(`.tab[data-tab='${tabId}']`).click();
      await expect(page.locator(`#${tabId}`)).toHaveClass(/act/);
    }
  });

  test("solo un tab debe estar activo a la vez", async ({ page }) => {
    for (const tabId of ["tab-whales", "tab-staking", "tab-governance", "tab-shadow"]) {
      await page.locator(`.tab[data-tab='${tabId}']`).click();
      await expect(page.locator(".tc.act")).toHaveCount(1);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════
// 3. STAKING (Content Locker)
// ═══════════════════════════════════════════════════════════════════

test.describe("Staking — Content Locker", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-staking']").click();
    await expect(page.locator("#tab-staking")).toHaveClass(/act/);
  });

  test("debe mostrar valores iniciales en cero", async ({ page }) => {
    await expect(page.locator("#stake-balance")).toContainText("0 TI");
    await expect(page.locator("#stake-locked")).toContainText("0 TI");
    await expect(page.locator("#stake-dividends")).toContainText("$0.00");
  });

  test("stakear tokens debe actualizar balance y locked", async ({ page }) => {
    await page.locator("#stake-amount").fill("5000");
    await clickStake(page);
    await expect(page.locator("#stake-balance")).toContainText("95,000 TI");
    await expect(page.locator("#stake-locked")).toContainText("5,000 TI");
  });

  test("stakear debe mostrar notificación de éxito", async ({ page }) => {
    await page.locator("#stake-amount").fill("5000");
    await clickStake(page);
    const notif = page.locator("#notif");
    await expect(notif).toHaveClass(/show/);
    await expect(notif).toContainText("Stakeado exitosamente");
  });

  test("unstakear tokens debe devolver balance", async ({ page }) => {
    await page.locator("#stake-amount").fill("10000");
    await clickStake(page);
    await expect(page.locator("#stake-locked")).toContainText("10,000 TI");

    await page.locator("#stake-amount").fill("3000");
    await clickUnstake(page);
    await expect(page.locator("#stake-locked")).toContainText("7,000 TI");
    await expect(page.locator("#stake-balance")).toContainText("93,000 TI");
  });

  test("múltiples stakings deben acumularse", async ({ page }) => {
    await page.locator("#stake-amount").fill("3000");
    await clickStake(page);
    await page.locator("#stake-amount").fill("7000");
    await clickStake(page);
    await expect(page.locator("#stake-locked")).toContainText("10,000 TI");
    await expect(page.locator("#stake-balance")).toContainText("90,000 TI");
  });

  test("cantidad inválida debe mostrar error", async ({ page }) => {
    await page.locator("#stake-amount").fill("-100");
    await clickStake(page);
    await expect(page.locator("#notif")).toHaveClass(/show/);
  });

  test("stakear más del balance debe mostrar error", async ({ page }) => {
    await page.locator("#stake-amount").fill("999999");
    await clickStake(page);
    await expect(page.locator("#notif")).toHaveClass(/show/);
    await expect(page.locator("#notif")).toContainText("No tienes suficientes");
  });

  test("unstakear sin tener staked debe mostrar error", async ({ page }) => {
    await page.locator("#stake-amount").fill("100");
    await clickUnstake(page);
    await expect(page.locator("#notif")).toHaveClass(/show/);
    await expect(page.locator("#notif")).toContainText("No tienes tokens stakados");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 4. STAKING + WHALE: contenido bloqueado por staking
// ═══════════════════════════════════════════════════════════════════

test.describe("Staking — Desbloqueo de Contenido", () => {
  test("flash loans deben estar bloqueados inicialmente en whale tab", async ({ page }) => {
    await page.locator(".tab[data-tab='tab-whales']").click();
    await expect(page.locator("#flash-opps .dc-lock-overlay")).toHaveCount(2);
    await expect(page.locator("#flash-opps .dc-lock-overlay").first()).toBeVisible();
  });

  test("stakear desbloquea flash loans en whale tab", async ({ page }) => {
    // Stakear desde el tab de staking
    await page.locator(".tab[data-tab='tab-staking']").click();
    await page.locator("#stake-amount").fill("5000");
    await clickStake(page);

    // Ir al whale tab y verificar que los overlays se ocultaron
    await page.locator(".tab[data-tab='tab-whales']").click();
    await expect(page.locator("#flash-opps .dc-lock-overlay").first()).not.toBeVisible();
  });

  test("unstakear todo rebloquea flash loans", async ({ page }) => {
    // Stakear
    await page.locator(".tab[data-tab='tab-staking']").click();
    await page.locator("#stake-amount").fill("5000");
    await clickStake(page);

    // Unstakear todo
    await page.locator("#stake-amount").fill("5000");
    await clickUnstake(page);

    // Ir al whale tab y verificar que los overlays volvieron
    await page.locator(".tab[data-tab='tab-whales']").click();
    await expect(page.locator("#flash-opps .dc-lock-overlay").first()).toBeVisible();
  });
});

// ═══════════════════════════════════════════════════════════════════
// 5. VOTING (Gobernanza)
// ═══════════════════════════════════════════════════════════════════

test.describe("Votación — Gobernanza", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-governance']").click();
    await expect(page.locator("#tab-governance")).toHaveClass(/act/);
  });

  test("debe mostrar las 3 propuestas PIP", async ({ page }) => {
    await expect(page.locator("#prop1")).toContainText("PIP-1");
    await expect(page.locator("#prop2")).toContainText("PIP-2");
    await expect(page.locator("#prop3")).toContainText("PIP-3");
  });

  test("prop1 debe tener barra de progreso inicial en 72%", async ({ page }) => {
    const style = await page.locator("#prop1-bar").getAttribute("style");
    expect(style).toContain("72%");
  });

  test("votar Sí debe incrementar la barra de progreso", async ({ page }) => {
    const initialStyle = await page.locator("#prop2-bar").getAttribute("style");
    await clickVote(page, "prop2", true);
    const newStyle = await page.locator("#prop2-bar").getAttribute("style");
    expect(newStyle).not.toBe(initialStyle);
  });

  test("votar debe mostrar notificación", async ({ page }) => {
    await clickVote(page, "prop1", true);
    await expect(page.locator("#notif")).toHaveClass(/show/);
    await expect(page.locator("#notif")).toContainText("Voto registrado");
  });

  test("votar No debe cambiar los porcentajes", async ({ page }) => {
    await clickVote(page, "prop2", false);
    await expect(page.locator("#prop2-yes")).toContainText("% a favor");
    await expect(page.locator("#prop2-no")).toContainText("% en contra");
  });

  test("múltiples votos deben acumularse", async ({ page }) => {
    for (let i = 0; i < 3; i++) await clickVote(page, "prop2", true);
    const style = await page.locator("#prop2-bar").getAttribute("style");
    expect(style).toContain("15%");
  });

  test("voto en prop1 no afecta prop2", async ({ page }) => {
    const before = await page.locator("#prop2-bar").getAttribute("style");
    await clickVote(page, "prop1", true);
    const after = await page.locator("#prop2-bar").getAttribute("style");
    expect(after).toBe(before);
  });

  test("barra no debe exceder 100%", async ({ page }) => {
    for (let i = 0; i < 20; i++) await clickVote(page, "prop2", true);
    const style = await page.locator("#prop2-bar").getAttribute("style");
    const pct = parseFloat(style.match(/([\d.]+)%/)[1]);
    expect(pct).toBeLessThanOrEqual(100);
  });

  test("debe mostrar historial de votaciones", async ({ page }) => {
    await expect(page.locator("text=Historial de Votaciones")).toBeVisible();
  });
});

// ═══════════════════════════════════════════════════════════════════
// 6. DASHBOARD & UI
// ═══════════════════════════════════════════════════════════════════

test.describe("Dashboard y UI", () => {
  test("debe mostrar distribución de tokens 51/35/14", async ({ page }) => {
    await expect(page.locator(".cd:has-text('510,000 TI')")).toBeVisible();
    await expect(page.locator(".cd:has-text('350,000 TI')")).toBeVisible();
    await expect(page.locator(".cd:has-text('140,000 TI')")).toBeVisible();
  });

  test("debe mostrar los 9 miembros de la familia", async ({ page }) => {
    await expect(page.locator(".mt li")).toHaveCount(9);
    await expect(page.locator(".mt li").first()).toContainText("Ramón & Nicolasa");
  });

  test("debe mostrar tabla de proyección de crecimiento", async ({ page }) => {
    const table = page.locator("#tab-dashboard table");
    await expect(table).toBeVisible();
    await expect(table).toContainText("Período");
    await expect(table).toContainText("Año 2");
  });

  test("hover no debe romper las tarjetas", async ({ page }) => {
    const card = page.locator(".cd").first();
    await card.hover();
    await expect(card).toBeVisible();
  });
});

// ═══════════════════════════════════════════════════════════════════
// 7. WHALE RADAR
// ═══════════════════════════════════════════════════════════════════

test.describe("Whale Radar", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-whales']").click();
    await expect(page.locator("#tab-whales")).toHaveClass(/act/);
  });

  test("debe mostrar las estadísticas del mempool", async ({ page }) => {
    await expect(page.locator("#mp-total-val")).toBeVisible();
    await expect(page.locator("#mp-tx-count")).toBeVisible();
    await expect(page.locator("#mp-gas-avg")).toBeVisible();
    await expect(page.locator("#mp-whale-count")).toBeVisible();
  });

  test("debe haber filas en el feed del mempool", async ({ page }) => {
    const count = await page.locator(".mp-row:not(.mp-row-head)").count();
    expect(count).toBeGreaterThan(0);
  });

  test("las oportunidades de flash loan deben estar bloqueadas", async ({ page }) => {
    await expect(page.locator("#flash-opps .dc-lock-overlay").first()).toBeVisible();
    await expect(page.locator("#flash-opps")).toContainText("Ballena Dorada");
    await expect(page.locator("#flash-opps .dc-lock-overlay")).toHaveCount(2);
  });
});

// ═══════════════════════════════════════════════════════════════════
// 8. WALLET
// ═══════════════════════════════════════════════════════════════════

test.describe("Conexión Wallet", () => {
  test.beforeEach(async ({ page }) => {
    await page.locator(".tab[data-tab='tab-wallet']").click();
    await expect(page.locator("#tab-wallet")).toHaveClass(/act/);
  });

  test("debe mostrar estado inicial desconectado", async ({ page }) => {
    await expect(page.locator("#wallet-status")).toContainText("No conectado");
  });

  test("debe mostrar botón de conectar MetaMask", async ({ page }) => {
    await expect(page.locator("#wallet-btn")).toContainText("Conectar MetaMask");
    await expect(page.locator("#wallet-info")).not.toBeVisible();
  });

  test("sin MetaMask debe mostrar mensaje de instalación", async ({ page }) => {
    await page.locator("#wallet-btn").click();
    await expect(page.locator("#wallet-status")).toContainText("MetaMask no instalado");
  });
});

// ═══════════════════════════════════════════════════════════════════
// 9. INTEGRACIÓN: Flujo Completo
// ═══════════════════════════════════════════════════════════════════

test.describe("Flujo Completo", () => {
  test("stakear → desbloquear → votar", async ({ page }) => {
    // 1. Stakear tokens
    await page.locator(".tab[data-tab='tab-staking']").click();
    await page.locator("#stake-amount").fill("10000");
    await clickStake(page);
    await expect(page.locator("#stake-locked")).toContainText("10,000 TI");

    // 2. Verificar que flash loans se desbloquearon en whale tab
    await page.locator(".tab[data-tab='tab-whales']").click();
    await expect(page.locator("#flash-opps .dc-lock-overlay").first()).not.toBeVisible();

    // 3. Votar en gobernanza
    await page.locator(".tab[data-tab='tab-governance']").click();
    await clickVote(page, "prop1", true);
    await expect(page.locator("#notif")).toHaveClass(/show/);
  });
});
