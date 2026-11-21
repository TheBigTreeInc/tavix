import test from 'node:test';
import assert from 'node:assert/strict';
import {publishingReadiness} from '../tools/studio-desktop/src/publishing-readiness.mjs';

const profile={githubRepository:'TheBigTreeInc/tavi-assets'};
const signedIn={authenticated:true};
const live={repository:profile.githubRepository,releases:[]};

test('no saved GitHub repository is not connected or authorized',()=>{
  const s=publishingReadiness(null,null,null,'');
  assert.equal(s.githubConfigured,false);
  assert.equal(s.mayInspectReleases,false);
  assert.equal(s.mayRequestGitHubWrite,false);
  assert.equal(s.officialAssetsPublishAuthorized,false);
});
test('configured repository without GitHub CLI login allows public inspection but no writes',()=>{
  const s=publishingReadiness(profile,{authenticated:false},live,profile.githubRepository);
  assert.equal(s.githubConfigured,true);
  assert.equal(s.liveFresh,true);
  assert.equal(s.mayInspectReleases,true);
  assert.equal(s.mayRequestGitHubWrite,false);
});
test('verified CLI login permits a request but does not grant official assets publication',()=>{
  const s=publishingReadiness(profile,signedIn,live,profile.githubRepository);
  assert.equal(s.mayRequestGitHubWrite,true);
  assert.equal(s.officialAssetsPublishAuthorized,false);
  assert.equal(s.remoteStorePublished,false);
  assert.equal(s.liveFresh,true);
});
test('unsaved repository change invalidates visible live status and blocks remote actions',()=>{
  const s=publishingReadiness(profile,signedIn,live,'TheBigTreeInc/redlink');
  assert.equal(s.pendingChanges,true);
  assert.equal(s.liveFresh,false);
  assert.equal(s.mayInspectReleases,false);
  assert.equal(s.mayRequestGitHubWrite,false);
});
test('live releases for a different repository are never shown as freshly fetched',()=>{
  const s=publishingReadiness(profile,signedIn,{repository:'TheBigTreeInc/redlink'},profile.githubRepository);
  assert.equal(s.liveFresh,false);
});
test('unverified authentication never activates write controls',()=>{
  const s=publishingReadiness(profile,null,null,profile.githubRepository);
  assert.equal(s.mayRequestGitHubWrite,false);
});

test('unsaved registry endpoint change also blocks release actions',()=>{
  const configured={githubRepository:'TheBigTreeInc/tavi-assets',assetsRegistryEndpoint:'https://registry.example.org'};
  const s=publishingReadiness(configured,signedIn,live,configured.githubRepository,'https://registry-two.example.org');
  assert.equal(s.pendingChanges,true);
  assert.equal(s.mayRequestGitHubWrite,false);
});
