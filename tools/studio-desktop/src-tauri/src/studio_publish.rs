//! Operator-controlled publication destinations and trusted native gateway.
//! Configuration alone is never authorization: LoopRD DAPI actions require a
//! verified scoped service principal and separate exact-artifact approval receipts.
use serde_json::{json, Value};
use std::{fs, io::Write, path::PathBuf};

fn profile_path() -> Result<PathBuf, String> {
    Ok(super::review::state_root()?.join("publication-destinations.json"))
}

fn valid_repository(value: &str) -> bool {
    if value.is_empty() { return true; }
    let pieces: Vec<&str> = value.split('/').collect();
    pieces.len()==2 && pieces.iter().all(|s| !s.is_empty() && s.len()<=80 &&
        s.bytes().all(|b| b.is_ascii_alphanumeric() || b==b'-' || b==b'_' || b==b'.'))
}

fn valid_endpoint(value: &str) -> bool {
    if value.is_empty() { return true; }
    if !value.starts_with("https://") || value.len()>180 || value.chars().any(|c| matches!(c,'@'|'?'|'#'|'\\'|' ')) { return false; }
    let host = &value[8..];
    !host.is_empty() && host.contains('.') && host.bytes().all(|b| b.is_ascii_alphanumeric() || b==b'-' || b==b'.') &&
        !host.starts_with('.') && !host.ends_with('.') && !host.contains("..")
}

fn valid_api_path(value: &str, tail: &str) -> bool {
    // Only relative paths on the operator-approved HTTPS host. No query, URL,
    // userinfo, traversal, escaped separators, redirects, or arbitrary domains.
    value.is_empty() || (value.len() <= 180 && value.starts_with('/') && value.ends_with(tail)
        && value.bytes().all(|b| b.is_ascii_alphanumeric() || matches!(b, b'/'|b'-'|b'_'|b'.'))
        && !value.contains("//") && !value.split('/').any(|p| p == "." || p == ".."))
}

fn load_profile() -> Result<(String,String,String,String),String> {
    let path = profile_path()?;
    if !path.exists() { return Ok((String::new(),String::new(),String::new(),String::new())); }
    let meta=path.symlink_metadata().map_err(|_| "Cannot inspect publishing destinations")?;
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len()>4096 { return Err("Unsafe publication configuration".into()); }
    let value:Value=serde_json::from_slice(&fs::read(path).map_err(|_| "Cannot read publishing destinations")?)
        .map_err(|_| "Invalid publishing destinations")?;
    if value.get("schema").and_then(Value::as_str)!=Some("tavix.studio.publication-destinations/v1") {
        return Err("Unsupported publication configuration".into());
    }
    let repo=value.get("githubRepository").and_then(Value::as_str).unwrap_or("");
    let endpoint=value.get("assetsRegistryEndpoint").and_then(Value::as_str).unwrap_or("");
    let admin=value.get("assetsRegistryAdminPath").and_then(Value::as_str).unwrap_or("");
    let catalog=value.get("assetsRegistryCatalogPath").and_then(Value::as_str).unwrap_or("");
    if !valid_repository(repo) || !valid_endpoint(endpoint) || !valid_api_path(admin,"/admin")
        || !valid_api_path(catalog,"/catalog") { return Err("Invalid saved publishing destinations".into()); }
    Ok((repo.into(),endpoint.into(),admin.into(),catalog.into()))
}

#[tauri::command]
pub(crate) fn studio_publishing_targets() -> Result<Value,String> {
    let (repo,endpoint,admin,catalog)=load_profile()?;
    Ok(json!({
        "schema":"tavix.studio.publication-readiness/v1",
        "githubRepository":repo, "assetsRegistryEndpoint":endpoint,
        "assetsRegistryAdminPath":admin,"assetsRegistryCatalogPath":catalog,
        "assetsRegistryPathsConfigured":!admin.is_empty() && !catalog.is_empty(),
        "githubConfigured":!repo.is_empty(), "assetsRegistryConfigured":!endpoint.is_empty(),
        "githubWriteAuthorized":false, "assetsPublishAuthorized":false,
        "developerPreviewDistributionConnected":false,
        "remotePublishAvailable":false,
        "nextSteps":[
            "Verify publisher identity and trusted GitHub application credentials outside the renderer",
            "Connect to LoopRD with verified DAPI paths and short-lived scoped service credentials supplied to the trusted native process",
            "Approve the exact artifact digest, catalog revision and release channel before committing",
            "Keep developer preview private and separate from official-store publication"
        ]
    }))
}

#[tauri::command]
pub(crate) fn studio_save_publishing_targets(github_repository:String, assets_registry_endpoint:String,
    assets_registry_admin_path:Option<String>, assets_registry_catalog_path:Option<String>) -> Result<Value,String> {
    let admin=assets_registry_admin_path.unwrap_or_default();
    let catalog=assets_registry_catalog_path.unwrap_or_default();
    if !valid_repository(&github_repository) || !valid_endpoint(&assets_registry_endpoint)
        || !valid_api_path(&admin,"/admin") || !valid_api_path(&catalog,"/catalog") {
        return Err("PUBLISH_DESTINATION_INVALID: Enter owner/repo and an HTTPS hostname without credentials or URL parameters".into());
    }
    let path=profile_path()?;
    if path.exists() {
        let meta=path.symlink_metadata().map_err(|_| "Cannot inspect publishing destinations")?;
        if !meta.is_file() || meta.file_type().is_symlink() {return Err("Unsafe publication configuration".into());}
    }
    let bytes=serde_json::to_vec_pretty(&json!({
        "schema":"tavix.studio.publication-destinations/v1",
        "githubRepository":github_repository,"assetsRegistryEndpoint":assets_registry_endpoint,
        "assetsRegistryAdminPath":admin,"assetsRegistryCatalogPath":catalog
    })).map_err(|_| "Cannot encode publishing destinations")?;
    let tmp=path.with_extension("json.new");
    let mut f=fs::OpenOptions::new().write(true).create_new(true).open(&tmp)
        .map_err(|_| "Cannot stage publication configuration")?;
    f.write_all(&bytes).map_err(|_| "Cannot write publication configuration")?;
    f.sync_all().map_err(|_| "Cannot save publication configuration")?;
    drop(f);
    if path.exists() {fs::remove_file(&path).map_err(|_| "Cannot replace publication configuration")?;}
    fs::rename(tmp,path).map_err(|_| "Cannot finish publication configuration".to_owned())?;
    studio_publishing_targets()
}

#[tauri::command]
pub(crate) fn studio_probe_publishing_targets() -> Result<Value,String> {
    // Probe ONLY operator-saved, strictly validated destinations. No URL, path,
    // credentials or request body ever comes from the untrusted renderer.
    let (repo,endpoint,_,_)=load_profile()?;
    super::review::script_call("publisher_probe", &[repo,endpoint])
}


// Live GitHub list is read-only; authenticated gh can additionally reveal drafts.
// No GitHub token or submitted package path can come from the renderer.
#[tauri::command]
pub(crate) fn studio_github_releases() -> Result<Value,String> {
    let (repo,_,_,_)=load_profile()?;
    if repo.is_empty() {return Err("PUBLISH_DESTINATION_INVALID: Save a GitHub repository first".into());}
    super::review::script_call("publisher_releases", &[repo])
}

#[tauri::command]
pub(crate) fn studio_github_auth() -> Result<Value,String> {
    super::review::script_call("publisher_auth", &[])
}

// Asset catalog and application release repository are separate destinations.
// Never permit an untrusted renderer to choose an arbitrary GitHub host/repo.
const ASSETS_CATALOG_REPO: &str = "TheBigTreeInc/tavi-assets";

#[tauri::command]
pub(crate) fn studio_github_login() -> Result<Value,String> {
    super::review::script_call("github_login", &[])
}

#[tauri::command]
pub(crate) fn studio_github_catalog_sync() -> Result<Value,String> {
    // Read-only: exact remote revision, editorial source and generated index.
    super::review::script_call("github_catalog_sync", &[ASSETS_CATALOG_REPO.into()])
}

#[tauri::command]
pub(crate) fn studio_github_catalog_preview(digest:String,base_revision:String) -> Result<Value,String> {
    let (source,record,kind)=approved_record(&digest)?;
    if kind!="tavia" {return Err("GITHUB_CATALOG_TAVIA_ONLY: Blueprints and applications do not belong in the Assets catalog".into());}
    super::review::script_call("github_catalog_preview", &[
        ASSETS_CATALOG_REPO.into(),source,record,digest,base_revision])
}

#[tauri::command]
pub(crate) fn studio_github_catalog_prepare(digest:String,base_revision:String,
    proposal_sha256:String,confirm_digest:String,operator_approved:bool) -> Result<Value,String> {
    if !operator_approved || confirm_digest!=digest || proposal_sha256.len()!=64 ||
       !proposal_sha256.bytes().all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase()) {
        return Err("GITHUB_CATALOG_CONFIRMATION_REQUIRED: Exact SHA-256 and an independent operator approval are required".into());
    }
    let (source,record,kind)=approved_record(&digest)?;
    if kind!="tavia" {return Err("GITHUB_CATALOG_TAVIA_ONLY: Only approved asset packs belong in the Assets catalog".into());}
    super::review::script_call("github_catalog_prepare", &[
        ASSETS_CATALOG_REPO.into(),source,record,digest,base_revision,proposal_sha256])
}

fn approved_record(digest: &str) -> Result<(String,String,String),String> {
    // Native review lookup does not trust a renderer-provided path or file name.
    if digest.len()!=64 || !digest.bytes().all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase()) {
        return Err("Invalid selected review digest".into());
    }
    let root=super::review::state_root()?;
    let path=root.join("reviews").join(format!("{digest}.json"));
    let meta=path.symlink_metadata().map_err(|_| "Review unavailable")?;
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len()>100000 {return Err("Review unavailable".into());}
    let report:Value=serde_json::from_slice(&fs::read(&path).map_err(|_| "Review unavailable")?)
        .map_err(|_| "Invalid review record")?;
    if report.get("sha256").and_then(Value::as_str)!=Some(digest) ||
        report.get("status").and_then(Value::as_str)!=Some("review_approved") ||
        report.get("canonicalValid").and_then(Value::as_bool)!=Some(true) ||
        report.get("storeReady").and_then(Value::as_bool)!=Some(true) {
        return Err("RELEASE_APPROVAL_REQUIRED: Exact local review approval is required".into());
    }
    let kind=report.get("kind").and_then(Value::as_str).ok_or("Invalid package type")?;
    if !["tavix","tavia"].contains(&kind) {return Err("Invalid package type".into());}
    let source=root.join("submissions").join(format!("{digest}.{kind}"));
    if !source.is_file() || source.symlink_metadata().map_err(|_| "Submitted archive unavailable")?.file_type().is_symlink() {
        return Err("Submitted archive unavailable".into());
    }
    Ok((source.to_string_lossy().to_string(),path.to_string_lossy().to_string(),kind.to_string()))
}

#[tauri::command]
pub(crate) fn studio_github_create_draft(digest:String,confirm_digest:String,public_distribution_approved:bool) -> Result<Value,String> {
    if !public_distribution_approved || confirm_digest!=digest {
        return Err("PUBLIC_DISTRIBUTION_CONFIRMATION_REQUIRED: Confirm the entire artifact digest and public-download intent".into());
    }
    let (repo,_,_,_)=load_profile()?;
    if repo.is_empty() {return Err("PUBLISH_DESTINATION_INVALID: Configure GitHub first".into());}
    let (source,record,_)=approved_record(&digest)?;
    super::review::script_call("publisher_draft", &[repo,source,record,digest])
}

#[tauri::command]
pub(crate) fn studio_github_publish_draft(digest:String,confirm_digest:String,public_distribution_approved:bool) -> Result<Value,String> {
    if !public_distribution_approved || confirm_digest!=digest {
        return Err("PUBLIC_DISTRIBUTION_CONFIRMATION_REQUIRED: Confirm the entire artifact digest and public-download intent".into());
    }
    let (repo,_,_,_)=load_profile()?;
    if repo.is_empty() {return Err("PUBLISH_DESTINATION_INVALID: Configure GitHub first".into());}
    let (source,record,_)=approved_record(&digest)?;
    super::review::script_call("publisher_publish", &[repo,source,record,digest])
}

#[tauri::command]
pub(crate) fn studio_github_release_receipt(digest:String) -> Result<Value,String> {
    let (repo,_,_,_)=load_profile()?;
    let (source,record,_)=approved_record(&digest)?;
    super::review::script_call("publisher_receipt", &[repo,source,record,digest])
}

fn looprd_urls() -> Result<(String,String,String),String> {
    let (_,host,admin,catalog)=load_profile()?;
    if host.is_empty() || admin.is_empty() || catalog.is_empty() {
        return Err("LOOPRD_DAPI_PATH_REQUIRED: Save the verified LoopRD /admin and /catalog paths first".into());
    }
    Ok((host,admin,catalog))
}

#[tauri::command]
pub(crate) fn studio_looprd_connect() -> Result<Value,String> {
    let (host,admin,catalog)=looprd_urls()?;
    // Check real scoped /catalog and /admin operations, not an unauthenticated HEAD.
    super::review::script_call("looprd_connect", &[host,admin,catalog])
}

#[tauri::command]
pub(crate) fn studio_looprd_catalog() -> Result<Value,String> {
    let (host,_,catalog)=looprd_urls()?;
    super::review::script_call("looprd_catalog", &[host,catalog])
}

#[tauri::command]
pub(crate) fn studio_looprd_inspect() -> Result<Value,String> {
    let (host,admin,_)=looprd_urls()?;
    super::review::script_call("looprd_inspect", &[host,admin])
}

fn exact_looprd_source(digest:&str, confirm_digest:&str, confirmed:bool) -> Result<(String,String),String> {
    if !confirmed || confirm_digest!=digest {
        return Err("LOOPRD_EXACT_APPROVAL_REQUIRED: Confirm the full artifact SHA-256".into());
    }
    let (source,record,kind)=approved_record(digest)?;
    if kind!="tavia" {return Err("LOOPRD_TAVIA_ONLY: Registry can only publish Tavi Assets packs".into());}
    Ok((source,record))
}

fn operator_receipt() -> Result<String,String> {
    let receipt=rfd::FileDialog::new().add_filter("Exact LoopRD operator receipt", &["json"])
        .pick_file().ok_or("LOOPRD_RECEIPT_REQUIRED: Select your independent approved JSON receipt")?;
    let metadata=receipt.symlink_metadata().map_err(|_| "LOOPRD_RECEIPT_REQUIRED")?;
    if !metadata.is_file() || metadata.file_type().is_symlink() || metadata.len()==0 || metadata.len()>4096 {
        return Err("LOOPRD_RECEIPT_INVALID: Choose an approved receipt of at most 4 KiB".into());
    }
    Ok(receipt.to_string_lossy().to_string())
}

#[tauri::command]
pub(crate) fn studio_looprd_stage(digest:String,confirm_digest:String,operator_approved:bool) -> Result<Value,String> {
    let (host,admin,_)=looprd_urls()?;
    let (source,record)=exact_looprd_source(&digest,&confirm_digest,operator_approved)?;
    let assets=super::studio_connection::assets_checkout().ok_or(
        "LOOPRD_CANONICAL_ASSETS_REQUIRED: Connect the canonical tavi-assets checkout first")?;
    let receipt=operator_receipt()?;
    super::review::script_call("looprd_stage", &[
        host,admin,source,record,digest,receipt,assets.to_string_lossy().to_string()])
}

#[tauri::command]
pub(crate) fn studio_looprd_publish(digest:String,confirm_digest:String,operator_approved:bool) -> Result<Value,String> {
    let (host,admin,_)=looprd_urls()?;
    let (source,record)=exact_looprd_source(&digest,&confirm_digest,operator_approved)?;
    let receipt=operator_receipt()?;
    super::review::script_call("looprd_publish", &[host,admin,source,record,digest,receipt])
}
