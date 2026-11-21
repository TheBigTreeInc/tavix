export function planBlueprintReview(kind:'tavix'|'tavia', previous:string, chosen:string):
  {action:'keep'|'recheck',blueprintId:string};
