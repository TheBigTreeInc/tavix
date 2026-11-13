/** Klondike 0.1.2 — optional, grant-scoped Tavi Assets card-back consumer.
 * The game NEVER installs packs, opens files, requests Wallet methods, or
 * synthesizes permissions. This module does not alter game rules or saves.
 */
import {createTaviAssetsClient} from './tavi-assets-client.mjs';

export const CARD_PACK = 'org.tavi.cards.standard';
export const CARD_CAPABILITY = 'card.back';
const FEATURE = 'tavi.assets/v1';
const MEDIA = new Set(['image/png','image/jpeg','image/webp','image/svg+xml']);
const BASE64 = /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/;

// Media type, pack/capability pair, encoding and size are all checked at the
// consumer boundary in addition to validation by the trusted host engine.
export function safeCardBack(result) {
  if (!result || result.schema !== 'tavi.assets.resource/v1' ||
      result.packId !== CARD_PACK || result.capability !== CARD_CAPABILITY ||
      result.encoding !== 'base64' || !MEDIA.has(result.contentType) ||
      typeof result.data !== 'string' || result.data.length < 4 ||
      result.data.length > 1_400_000 || !BASE64.test(result.data)) {
    throw new Error('Invalid or unauthorized Tavi Assets card back');
  }
  return `url("data:${result.contentType};base64,${result.data}")`;
}

/** Dependency injection permits independent tests; only the host SDK issues
 * requests in production. A snapshot is deliberately NOT persisted as a game
 * save, because access is session/account scoped and may be revoked.
 */
export function createKlondikeAssetController({host, root, documentRef, windowRef, assets = null}) {
  if (!host || !root || !documentRef || !windowRef) throw new TypeError('Tavi host and document required');
  const client = assets ?? createTaviAssetsClient({
    info: () => host.info(),
    request: (method, params) => host.call(method, params)
  });
  let generation = 0;
  let running = false;
  function clear() {
    root.removeAttribute('data-tavi-card-back');
    root.style.removeProperty('--tavi-card-back-image');
  }
  async function refresh() {
    const ticket = ++generation;
    clear();
    try {
      const info = await host.info();
      if (!info || !Array.isArray(info.features) || !info.features.includes(FEATURE)) return false;
      const permissions = await host.capabilities();
      if (!Array.isArray(permissions) || !permissions.includes('assets.read')) return false;
      await client.connect();
      const image = safeCardBack(await client.resolve(CARD_PACK, CARD_CAPABILITY));
      if (ticket !== generation || !running) return false;
      root.style.setProperty('--tavi-card-back-image', image);
      root.setAttribute('data-tavi-card-back', 'granted');
      return true;
    } catch {
      if (ticket === generation) clear();
      return false;
    }
  }
  function onVisible() { if (running && documentRef.visibilityState === 'visible') void refresh(); }
  function onFocus() { if (running) void refresh(); }
  function dispose() {
    running = false;
    generation += 1;
    documentRef.removeEventListener('visibilitychange', onVisible);
    windowRef.removeEventListener('focus', onFocus);
    windowRef.removeEventListener('pagehide', dispose);
    clear();
    if (typeof host.dispose === 'function') host.dispose();
  }
  function start() {
    if (running) return Promise.resolve(false);
    running = true;
    documentRef.addEventListener('visibilitychange', onVisible);
    windowRef.addEventListener('focus', onFocus);
    windowRef.addEventListener('pagehide', dispose);
    return refresh();
  }
  return Object.freeze({start, refresh, dispose});
}
