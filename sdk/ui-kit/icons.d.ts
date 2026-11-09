export declare const TAVIX_ICON_SET:'tavix.icons/v1';
export type TaviIconName='chevron-right'|'search'|'user-round'|'users-round'|'monitor'|'palette'|'shield'|'database'|'info'|'eye'|'volume-2'|'refresh-cw'|'key-round'|'log-out'|'download'|'chart-no-axes-column'|'arrow-left'|'house'|'send'|'circle-question-mark'|'minus'|'message-square-text'|'gamepad-2'|'wallet'|'bell'|'paw-print'|'store'|'user-round-plus'|'settings'|'puzzle'|'landmark'|'notebook-pen'|'layout-grid'|'star'|'folder'|'folder-open'|'file'|'file-text'|'save'|'pencil'|'trash-2'|'plus'|'x'|'menu'|'check'|'chevron-down'|'chevron-left'|'external-link'|'upload'|'sliders-horizontal';
export type TaviIconSize='sm'|'md'|'lg'|'xl';
export declare const TAVIX_ICON_NAMES:readonly TaviIconName[];
export declare const TAVIX_ICON_SIZES:Readonly<Record<TaviIconSize,number>>;
export declare function hasTaviIcon(name:unknown):name is TaviIconName;
export declare function createTaviIcon(name:TaviIconName,options?:{size?:TaviIconSize;decorative?:boolean;label?:string;documentRef?:Document}):SVGSVGElement;
