export type PublicationRow = {key:string;name:string;id:string;version:string;type:string;kind:string;source:string;review:string;live:string;editable:boolean;eligible:boolean};
export type PublicationDraft = {priceGold:number|null;listed:boolean;testing:boolean;summary:string};
export function publicationRows(reviews:any[],published:any[],inspected:any[],registryChecked:boolean):PublicationRow[];
export function cleanDraft(value:any):PublicationDraft;
export function draftEquals(a:any,b:any):boolean;
