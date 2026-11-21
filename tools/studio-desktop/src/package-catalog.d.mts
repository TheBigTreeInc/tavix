export type Candidate = {id:string; name:string; version:string; classification:'game'|'app'};
export type PackageGroup = {id:string; name:string; classification:'game'|'app'; versions:Candidate[]};
export function compareVersions(left:string,right:string):number;
export function groupPackages(packages:Candidate[]):PackageGroup[];
