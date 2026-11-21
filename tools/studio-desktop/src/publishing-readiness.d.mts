export interface PublishingReadiness {
  githubConfigured:boolean; pendingChanges:boolean; githubAuthenticated:boolean; liveFresh:boolean;
  mayInspectReleases:boolean; mayRequestGitHubWrite:boolean;
  officialAssetsPublishAuthorized:boolean; remoteStorePublished:boolean;
}
export function publishingReadiness(profile:{githubRepository?:string;assetsRegistryEndpoint?:string}|null,
  auth:{authenticated:boolean}|null, live:{repository:string}|null, editedRepo:string, editedEndpoint?:string):PublishingReadiness;
