import test from 'node:test';
import assert from 'node:assert/strict';
import {planBlueprintReview} from '../tools/studio-desktop/src/blueprint-review-action.mjs';

test('new custom TAVIA stays unmapped with no recheck',()=>{
  assert.deepEqual(planBlueprintReview('tavia','',''),{action:'keep',blueprintId:''});
});
test('choosing a profile triggers exact retained-package recheck',()=>{
  assert.deepEqual(planBlueprintReview('tavia','','local-tarot'),{action:'recheck',blueprintId:'local-tarot'});
});
test('changing a previously selected blueprint triggers recheck',()=>{
  assert.deepEqual(planBlueprintReview('tavia','a','b'),{action:'recheck',blueprintId:'b'});
});
test('clearing an old blueprint resets prior review via empty recheck',()=>{
  assert.deepEqual(planBlueprintReview('tavia','a',''),{action:'recheck',blueprintId:''});
});
test('unchanged blueprint does not recheck',()=>{
  assert.deepEqual(planBlueprintReview('tavia','a','a'),{action:'keep',blueprintId:'a'});
});
test('apps never acquire asset blueprint authority',()=>{
  assert.deepEqual(planBlueprintReview('tavix','','local-tarot'),{action:'keep',blueprintId:''});
});
test('non-string selections fail closed',()=>{
  assert.throws(()=>planBlueprintReview('tavia','','not valid'?null:null), TypeError);
});
