import React, {useMemo, useState} from 'react';
import {Button, Card, CardBody, CardTitle, Label} from '@patternfly/react-core';
import {groupPackages, type Candidate} from './package-catalog.mjs';

export function PackageSelector({packages}:{packages:Candidate[]}) {
  const groups=useMemo(()=>groupPackages(packages),[packages]);
  const [selectedId,setSelectedId]=useState('');
  const [chosenVersions,setChosenVersions]=useState<Record<string,string>>({});
  const [search,setSearch]=useState('');
  const filter=search.trim().toLocaleLowerCase();
  const visible=groups.filter(g=>!filter||
    g.name.toLocaleLowerCase().includes(filter)||g.id.toLocaleLowerCase().includes(filter));
  const selected=visible.find(g=>g.id===selectedId)||visible[0];
  const chosen=selected?.versions.find(v=>v.version===chosenVersions[selected.id])||selected?.versions[0];
  return <Card><CardTitle>Games & applications — source candidates</CardTitle><CardBody>
    <p>Select a game or app, then choose the exact version to inspect. These are repository candidates, not installed Tavi client packages or official publication approvals.</p>
    {groups.length===0?<p>No release manifests found.</p>:<div className="studio-package-picker">
      <div className="studio-package-left">
        <label htmlFor="studio-package-search">Find a game or app</label>
        <input id="studio-package-search" type="search" className="studio-publish-input" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by name or identifier"/>
        <nav aria-label="Select game or application" className="studio-package-list">
          {visible.map(group=><Button key={group.id} isBlock className="studio-package-choice"
            variant={selected?.id===group.id?'primary':'secondary'}
            aria-current={selected?.id===group.id?'true':undefined}
            onClick={()=>setSelectedId(group.id)}>
            <span className="studio-package-choice-name">{group.name}</span>
            <span className="studio-package-choice-meta">{group.classification==='game'?'Game':'App'} · {group.versions.length} {group.versions.length===1?'version':'versions'}</span>
          </Button>)}
          {visible.length===0&&<p>No games or apps match this search.</p>}
        </nav>
      </div>
      <section className="studio-package-detail" aria-label="Selected package details">
        {selected&&chosen? <>
          <div className="studio-package-detail-heading"><strong>{selected.name}</strong><Label>{selected.classification==='game'?'Game':'App'}</Label></div>
          <p className="studio-mono">{selected.id}</p>
          <label htmlFor="studio-package-version"><strong>Choose version</strong></label>
          <select id="studio-package-version" className="studio-select" value={chosen.version}
            onChange={e=>setChosenVersions(previous=>({...previous,[selected.id]:e.target.value}))}>
            {selected.versions.map(version=><option key={version.version} value={version.version}>{version.version}</option>)}
          </select>
          <p className="studio-muted">Newest source version is selected by default. Earlier releases remain available.</p>
          <dl className="studio-package-metadata">
            <dt>Version</dt><dd>{chosen.version}</dd>
            <dt>Classification</dt><dd>{chosen.classification==='game'?'Game':'App'}</dd>
            <dt>Package identifier</dt><dd className="studio-mono">{chosen.id}</dd>
            <dt>Available versions</dt><dd>{selected.versions.length}</dd>
          </dl>
          <p className="studio-muted">Read-only manifest inventory. Import and review the original archive separately in Submission review.</p>
        </>:<p>Select a listed game or app to inspect its versions.</p>}
      </section>
    </div>}
  </CardBody></Card>;
}
