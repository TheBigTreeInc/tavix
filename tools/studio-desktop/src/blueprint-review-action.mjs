/** Pure UI transition plan: a review blueprint is a validator profile,
 * not an entitlement, publisher permission, or mutation of the .tavia bytes. */
export function planBlueprintReview(kind,previous,chosen){
  if(kind!=='tavia')return {action:'keep',blueprintId:''};
  if(typeof previous!=='string'||typeof chosen!=='string')throw new TypeError('invalid blueprint choice');
  if(previous===chosen)return {action:'keep',blueprintId:chosen};
  return {action:'recheck',blueprintId:chosen};
}
