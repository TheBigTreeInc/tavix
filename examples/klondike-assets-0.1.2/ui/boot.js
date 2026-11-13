/**
 * Boot script: creates the application once the DOM is ready.
 * Kept separate from the bundled library so the bundle stays reusable.
 */
(function () {
  'use strict';

  function boot() {
    var K = window.Klondike;
    if (!K || !K.App) {
      document.getElementById('status').textContent = 'The game failed to load.';
      return;
    }
    var app = K.App.createApp({
      Game: K.Game,
      Serialize: K.Serialize,
      Storage: K.Storage,
      TaviXHost: K.TaviXHost,
      TaviXAssets: K.TaviXAssets,
      // The card-back integration is initialized separately after the game
      // boots, keeping offline gameplay independent from host asset access.
      assetsProvider: null,
      Renderer: K.Renderer,
      Input: K.Input,
      elements: {
        board: document.getElementById('board'),
        stock: document.getElementById('stock'),
        waste: document.getElementById('waste'),
        foundations: document.getElementById('foundations'),
        tableau: document.getElementById('tableau'),
        status: document.getElementById('status'),
        toast: document.getElementById('toast'),
        undoButton: document.getElementById('btn-undo'),
        newButton: document.getElementById('btn-new'),
        restartButton: document.getElementById('btn-restart'),
        themeButton: document.getElementById('btn-theme'),
        ruleButton: document.getElementById('btn-rules')
      }
    });
    window.klondikeApp = app;
    app.start();
    // Optional, host-negotiated cosmetic. Never block the offline game on imports,
    // permissions, asset downloads or UI startup. No credential/pack registry here.
    if (K.TaviXHost && K.TaviXHost.isHostContext()) {
      import('./asset-integration.mjs').then(function (module) {
        var controller = module.createKlondikeAssetController({
          host: K.TaviXHost.createClient(),
          root: document.documentElement,
          documentRef: document,
          windowRef: window
        });
        window.klondikeAssets = controller;
        controller.start();
      }).catch(function () { /* Bundled cards remain playable. */ });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
}());
