/** Apply bounded, non-sensitive host appearance context to an app's own root. */
export function applyTaviUI(root, context) {
 if (!root?.dataset || context?.schema !== 'tavix.ui/v1') throw Error('Invalid Tavi UI context');
 root.dataset.taviTheme = context.theme === 'dark' ? 'dark' : 'light';
 root.dataset.taviDevice = ['phone', 'tablet', 'desktop'].includes(context.device) ? context.device : 'phone';
 root.dataset.taviOrientation = context.orientation === 'landscape' ? 'landscape' : 'portrait';
 root.dataset.taviChatPlacement = context.chat?.placement === 'left' ? 'left' : 'center';
 return root;
}

/**
 * Keep an app's typography and responsive controls synchronized with its *own*
 * viewport and, if advertised by a trusted SDK transport, host theme changes.
 *
 * The host's device label (desktop/tablet/phone) describes the platform, not
 * the width of a detached or split application window. `data-tavi-layout` is
 * based on this actual local viewport and NEVER requests additional privileges.
 * `ready` resolves to {source:'host'|'local'}; failure to connect is harmless.
 * The caller owns the SDK and must dispose it separately.
 */
export function createTaviUIController(root, {sdk = null, windowRef = globalThis.window,
 ResizeObserverClass = globalThis.ResizeObserver} = {}) {
 if (!root?.dataset) throw new TypeError('Tavi UI root must have a dataset');
 let disposed = false;
 let hostContext = null;
 let unsubscribe = null;
 let observer = null;
 let revision = 0;
 const media = windowRef?.matchMedia?.('(prefers-color-scheme: dark)') || null;
 const width = () => {
  const own = Number(root.clientWidth);
  if (Number.isFinite(own) && own > 0) return own;
  const w = Number(windowRef?.innerWidth);
  return Number.isFinite(w) && w > 0 ? w : 355;
 };
 const height = () => {
  const h = Number(windowRef?.innerHeight);
  return Number.isFinite(h) && h > 0 ? h : 630;
 };
 function localContext() {
  const w = width(), h = height();
  return {schema:'tavix.ui/v1',theme:media?.matches?'dark':'light',
   device:w < 600?'phone':w < 960?'tablet':'desktop',
   orientation:w > h?'landscape':'portrait',chat:{placement:'center'}};
 }
 function updateLayout() {
  if (disposed) return;
  const w = width();
  const layout = w < 600?'compact':w < 960?'medium':'wide';
  if (root.dataset.taviLayout !== layout) root.dataset.taviLayout = layout;
 }
 function refresh() {
  if (disposed) return;
  applyTaviUI(root,hostContext || localContext());
  updateLayout();
 }
 function handleHostContext(context) {
  if (disposed || context?.schema !== 'tavix.ui/v1') return;
  ++revision;
  hostContext = context;
  refresh();
 }
 refresh();
 if (typeof ResizeObserverClass === 'function') {
  observer = new ResizeObserverClass(updateLayout);
  observer.observe(root);
 } else windowRef?.addEventListener?.('resize',refresh);
 // A browser can change its OS theme while the app is running in local preview.
 const themeChanged = () => {if (!hostContext) refresh();};
 if (media?.addEventListener) media.addEventListener('change',themeChanged);
 else media?.addListener?.(themeChanged);
 const ready = (async () => {
  if (!sdk) return {source:'local'};
  try {
   if (typeof sdk.info !== 'function' || typeof sdk.uiContext !== 'function' || typeof sdk.on !== 'function')
    return {source:'local'};
   const info = await sdk.info();
   if (disposed || !Array.isArray(info?.features) || !info.features.includes('tavix.ui/v1'))
    return {source:'local'};
   // Subscribe before requesting the snapshot; a newer event wins over it.
   const before = revision;
   unsubscribe = sdk.on('ui.contextChanged',handleHostContext);
   const context = await sdk.uiContext();
   if (disposed) {unsubscribe?.();unsubscribe=null;return {source:'local'};}
   if (revision === before && context?.schema === 'tavix.ui/v1') handleHostContext(context);
   return {source:hostContext?'host':'local'};
  } catch {
   // A missing or denied optional read-only UI capability is not a startup error.
   unsubscribe?.();unsubscribe=null;
   return {source:'local'};
  }
 })();
 return {
  ready,
  refresh,
  dispose() {
   if (disposed) return;
   disposed = true;
   unsubscribe?.();unsubscribe = null;
   observer?.disconnect();
   windowRef?.removeEventListener?.('resize',refresh);
   if (media?.removeEventListener) media.removeEventListener('change',themeChanged);
   else media?.removeListener?.(themeChanged);
  }
 };
}
