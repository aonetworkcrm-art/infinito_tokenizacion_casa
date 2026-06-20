/**
 * 🎭 Playwright Configuration — Proyecto Infinito
 * ================================================
 * Configuración unificada para:
 *   - 44 tests funcionales (test_dapp_frontend.spec.js)
 *   - Visual regression tests (test_visual_regression.spec.js)
 *
 * Ejecutar:
 *   npx playwright test                     # modo normal
 *   npx playwright test --update-snapshots  # generar/actualizar baselines
 *   npx playwright test --reporter=list     # verbose
 */

const { defineConfig } = require("@playwright/test");
const path = require("path");

module.exports = defineConfig({
  /* Directorio donde están los tests */
  testDir: path.join(__dirname, "tests"),

  /* Timeout por test */
  timeout: 30000,

  /* Timeout por expect (assertions) */
  expect: {
    timeout: 10000,

    /* Configuración de screenshots para visual regression */
    toHaveScreenshot: {
      /* Tolerancia máxima de diferencia de píxeles (0 = exacto) */
      maxDiffPixelRatio: 0.02,
      /* Área de recorte opcional para ignorar scrollbars, etc. */
      threshold: 0.2,
      /* Animaciones: congelar GIFs, videos, y transiciones CSS */
      animations: "disabled",
      /* Scrollbar: ocultar para evitar falsos positivos */
      caret: "hide",
    },
  },

  /* Fallar rápido si un test falla */
  maxFailures: 10,

  /* No usar workers paralelos para visual regression (orden consistente) */
  workers: 1,

  /* Reintentar tests de visual regression 2 veces en CI */
  retries: process.env.CI ? 2 : 0,

  /* Reporters */
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report" }],
  ],

  /* Proyectos */
  projects: [
    {
      name: "chromium",
      use: {
        browserName: "chromium",

        /* Viewport fijo para screenshots consistentes */
        viewport: { width: 1440, height: 900 },

        /* Locale para fechas consistentes */
        locale: "es-DO",

        /* Timezone para clock consistente */
        timezoneId: "America/Santo_Domingo",

        /* Ignorar errores de HTTPS (no relevante aquí) */
        ignoreHTTPSErrors: true,

        /* Tomar screenshot en failures */
        screenshot: "only-on-failure",

        /* Traza en failures (útil para debug en CI) */
        trace: "on-first-retry",

        /* Ocultar scrollbars en screenshots */
        colorScheme: "dark",
      },
    },
  ],

  /* Directorio de salida para snapshots de visual regression */
  snapshotPathTemplate: path.join(
    __dirname,
    "tests",
    "snapshots",
    "{projectName}",
    "{arg}{ext}"
  ),

  /* Limpiar output entre runs */
  outputDir: path.join(__dirname, "test-results"),
});
