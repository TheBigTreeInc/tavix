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
      // The shared assets runtime adapter is injected by the host
      // integration. Without it the game simply has no assets, which is a
      // supported state: the game never needs them to be played.
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
}());
