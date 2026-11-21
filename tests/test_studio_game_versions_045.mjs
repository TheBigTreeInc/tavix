import assert from 'node:assert/strict';
import test from 'node:test';
import {compareVersions,groupPackages} from '../tools/studio-desktop/src/package-catalog.mjs';

const row=(id,version,classification='game',name=id)=>({id,version,classification,name});
test('numeric versions are sorted newest first rather than alphabetically',()=>{
  const groups=groupPackages([row('g','1.9.0'),row('g','1.10.0'),row('g','1.2.0')]);
  assert.equal(groups.length,1);
  assert.deepEqual(groups[0].versions.map(v=>v.version),['1.10.0','1.9.0','1.2.0']);
});
test('stable semver outranks prerelease; prerelease identifiers follow semver rules',()=>{
  assert.ok(compareVersions('2.0.0','2.0.0-rc.3')>0);
  assert.ok(compareVersions('2.0.0-rc.10','2.0.0-rc.2')>0);
  assert.ok(compareVersions('2.0.0-beta','2.0.0-2')>0);
  assert.ok(compareVersions('2.0.0-rc.1','2.0.0-rc.1.2')<0);
});
test('one selectable entry per package identity; retains all unique versions',()=>{
  const groups=groupPackages([
    row('app.alpha','0.1.0','app','Alpha'),row('game.beta','0.2.0','game','Beta'),
    row('game.beta','0.1.0','game','Old Beta'),row('game.beta','0.2.0','game','Duplicate'),
    row('game.delta','1.0.0','game','Delta'),row('app.alpha','0.2.0','app','Alpha')
  ]);
  assert.deepEqual(groups.map(g=>g.id),['game.beta','game.delta','app.alpha']);
  assert.deepEqual(groups[0].versions.map(v=>v.version),['0.2.0','0.1.0']);
  assert.equal(groups[0].name,'Beta');
  assert.equal(groups[0].classification,'game');
});
test('empty, nonsemver and missing rows remain safe and inspectable',()=>{
  assert.deepEqual(groupPackages([]),[]);
  assert.deepEqual(groupPackages([row('g','preview'),row('g','preview2'),{},null]).map(g=>g.versions.length),[2]);
});
