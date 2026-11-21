// Pure, read-only presentation helpers for Studio's bounded source inventory.
// Never infer publication, installation or a user's entitlement from these rows.
const natural = new Intl.Collator('en', {numeric:true, sensitivity:'base'});

function semverParts(value) {
  const match = /^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$/.exec(value);
  if (!match) return null;
  return {numbers:match.slice(1,4).map(BigInt), pre:match[4]||''};
}

function comparePre(left,right) {
  if (!left && !right) return 0;
  if (!left) return 1; // Final releases rank after their prereleases.
  if (!right) return -1;
  const a=left.split('.'), b=right.split('.');
  for(let i=0;i<Math.min(a.length,b.length);i++) {
    const aa=/^\d+$/.test(a[i]), bb=/^\d+$/.test(b[i]);
    if(aa && bb) {
      const difference=BigInt(a[i]) - BigInt(b[i]);
      if (difference) return difference>0n?1:-1;
    } else if(aa!==bb) return aa?-1:1;
    else {const c=a[i].localeCompare(b[i],'en'); if(c) return Math.sign(c);}
  }
  return Math.sign(a.length-b.length);
}

export function compareVersions(left,right) {
  const a=semverParts(left), b=semverParts(right);
  if(a && b) {
    for(let i=0;i<3;i++) {
      if(a.numbers[i]!==b.numbers[i]) return a.numbers[i]>b.numbers[i]?1:-1;
    }
    return comparePre(a.pre,b.pre);
  }
  return natural.compare(left,right);
}

export function groupPackages(packages) {
  const grouped=new Map();
  for(const pkg of packages) {
    if(!pkg || !pkg.id || !pkg.version) continue;
    let group=grouped.get(pkg.id);
    if(!group) {group={id:pkg.id,name:pkg.id,classification:'app',versions:[]};grouped.set(pkg.id,group);}
    // Identical id/version rows are not distinct choices, even if returned twice.
    if(!group.versions.some(v=>v.version===pkg.version)) group.versions.push(pkg);
  }
  for (const group of grouped.values()) {
    group.versions.sort((a,b)=>compareVersions(b.version,a.version));
    const mostRecent=group.versions[0];
    group.name=mostRecent.name||group.id;
    group.classification=mostRecent.classification==='game'?'game':'app';
  }
  return [...grouped.values()].sort((a,b)=>
    (a.classification===b.classification?0:a.classification==='game'?-1:1)
    || natural.compare(a.name,b.name) || natural.compare(a.id,b.id));
}
