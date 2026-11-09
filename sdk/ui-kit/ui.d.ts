export interface TaviXUIContext {schema:'tavix.ui/v1';theme:'light'|'dark';device:'phone'|'tablet'|'desktop';orientation:'portrait'|'landscape';chat?:{placement:'left'|'center'}}
export declare function applyTaviUI(root:HTMLElement,context:TaviXUIContext):HTMLElement;
export type TaviUILayout='compact'|'medium'|'wide';
export interface TaviUIBridgeSDK {
 info():Promise<{features?:string[]}>;
 uiContext():Promise<TaviXUIContext>;
 on(event:'ui.contextChanged',callback:(context:TaviXUIContext)=>void):()=>void;
}
export interface TaviUIController {
 readonly ready:Promise<{source:'host'|'local'}>;
 refresh():void;
 dispose():void;
}
export declare function createTaviUIController(root:HTMLElement,options?:{
 sdk?:TaviUIBridgeSDK|null;
 windowRef?:Window;
 ResizeObserverClass?:typeof ResizeObserver;
}):TaviUIController;
