/** Presentation-only publishing readiness. Never a permission/grant source. */
export function publishingReadiness(profile, auth, live, editedRepo, editedEndpoint) {
  const savedRepo = typeof profile?.githubRepository === 'string' ? profile.githubRepository : '';
  const githubConfigured = Boolean(savedRepo);
  const savedEndpoint = typeof profile?.assetsRegistryEndpoint === 'string' ? profile.assetsRegistryEndpoint : '';
  const pendingChanges = editedRepo !== savedRepo || (editedEndpoint !== undefined && editedEndpoint !== savedEndpoint);
  const githubAuthenticated = auth?.authenticated === true;
  const liveFresh = Boolean(live?.repository === savedRepo && githubConfigured && !pendingChanges);
  return Object.freeze({
    githubConfigured, pendingChanges, githubAuthenticated, liveFresh,
    mayInspectReleases: githubConfigured && !pendingChanges,
    mayRequestGitHubWrite: githubConfigured && !pendingChanges && githubAuthenticated,
    // These remain separate from GitHub and never derive from a local review.
    officialAssetsPublishAuthorized: false,
    remoteStorePublished: false
  });
}
