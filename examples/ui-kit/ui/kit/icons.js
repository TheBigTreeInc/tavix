/** TaviX UI icon kit. Static, locally vetted shapes. No network or host privileges. */
import {LUCIDE_ICONS} from './icon-shapes.js';
export const TAVIX_ICON_SET='tavix.icons/v1';
export const TAVIX_ICON_NAMES=Object.freeze(Object.keys(LUCIDE_ICONS));
export const TAVIX_ICON_SIZES=Object.freeze({sm:16,md:20,lg:24,xl:32});
export const hasTaviIcon=name=>typeof name==='string'&&Object.hasOwn(LUCIDE_ICONS,name);
/** Return a new SVG node. A label is mandatory for meaningful (nondecorative) icons.
 * Icon-only buttons still require an accessible name on the button itself.
 */
export function createTaviIcon(name,{size='md',decorative=true,label='',documentRef=globalThis.document}={}){
 if(!hasTaviIcon(name))throw new RangeError('Unknown Tavi icon');
 if(!Object.hasOwn(TAVIX_ICON_SIZES,size))throw new RangeError('Unknown Tavi icon size');
 if(!decorative&&(typeof label!=='string'||!label.trim()))throw new TypeError('Accessible icon label required');
 if(!documentRef?.createElementNS)throw new TypeError('A DOM document is required');
 const svg=documentRef.createElementNS('http://www.w3.org/2000/svg','svg');
 svg.setAttribute('viewBox','0 0 24 24');
 svg.setAttribute('fill','none');svg.setAttribute('stroke','currentColor');
 svg.setAttribute('stroke-width','2');svg.setAttribute('stroke-linecap','round');
 svg.setAttribute('stroke-linejoin','round');svg.setAttribute('focusable','false');
 svg.setAttribute('class',`tavix-icon tavix-icon--${size}`);
 if(decorative)svg.setAttribute('aria-hidden','true');
 else{svg.setAttribute('role','img');svg.setAttribute('aria-label',label.trim());}
 // Only exact, reviewed, bundled static paths reach the SVG parser.
 svg.innerHTML=LUCIDE_ICONS[name];
 return svg;
}
