//! Local, operator-selected Tavi Assets source connection and read-only health.
//! Local filesystem preferences are not an extension grant or remote credential.
use serde_json::{json, Value};
use std::{fs, path::{Path, PathBuf}};

fn preference_path() -> Result<PathBuf, String> {
    Ok(super::review::state_root()?.join("assets-source.json"))
}

fn verify_assets(candidate: &Path) -> Option<PathBuf> {
    let root = candidate.canonicalize().ok()?;
    let manifest = root.join("project.zr");
    let metadata = manifest.symlink_metadata().ok()?;
    if !metadata.is_file() || metadata.file_type().is_symlink() || metadata.len() > 65536 {
        return None;
    }
    let descriptor: Value = serde_json::from_slice(&fs::read(manifest).ok()?).ok()?;
    if descriptor.get("project_key").and_then(Value::as_str) != Some("tavi-assets") {
        return None;
    }
    let validator = root.join("src/tavi_assets/tavia.py");
    let source = validator.symlink_metadata().ok()?;
    if !source.is_file() || source.file_type().is_symlink() || source.len() > 100000 {
        return None;
    }
    Some(root)
}

fn saved_preference() -> Option<PathBuf> {
    let file = preference_path().ok()?;
    let info = file.symlink_metadata().ok()?;
    if !info.is_file() || info.file_type().is_symlink() || info.len() > 4096 {
        return None;
    }
    let data: Value = serde_json::from_slice(&fs::read(file).ok()?).ok()?;
    if data.get("schema").and_then(Value::as_str) != Some("tavix.studio.assets-source/v1") {
        return None;
    }
    Some(PathBuf::from(data.get("root")?.as_str()?))
}

pub(crate) fn assets_checkout() -> Option<PathBuf> {
    // An explicit invalid preference fails closed. Don't silently use another checkout.
    if let Ok(file) = preference_path() {
        if file.exists() { return saved_preference().and_then(|p| verify_assets(&p)); }
    }
    if let Some(selected) = std::env::var_os("TAVI_ASSETS_ROOT") {
        return verify_assets(&PathBuf::from(selected));
    }
    super::root_dir().and_then(|root| verify_assets(&root.join("../tavi-assets")))
}

fn source_kind() -> &'static str {
    if preference_path().map(|p| p.exists()).unwrap_or(false) { "operator" }
    else if std::env::var_os("TAVI_ASSETS_ROOT").is_some() { "environment" }
    else { "sibling" }
}

#[tauri::command]
pub(crate) fn studio_health() -> Result<Value, String> {
    let root = assets_checkout();
    let source = source_kind();
    let args = vec![root.map(|v| v.to_string_lossy().to_string()).unwrap_or("-".into()),source.into()];
    super::review::script_call("health", &args)
}

#[tauri::command]
pub(crate) fn studio_connect_assets() -> Result<Value, String> {
    let selected = rfd::FileDialog::new().pick_folder().ok_or("Connection cancelled")?;
    let root = verify_assets(&selected).ok_or("ASSETS_SOURCE_INVALID: Select the tavi-assets project root containing project.zr and src/tavi_assets/tavia.py")?;
    let target = preference_path()?;
    if target.exists() {
        let meta = target.symlink_metadata().map_err(|_| "Cannot inspect Assets preference")?;
        if !meta.is_file() || meta.file_type().is_symlink() { return Err("Unsafe Assets preference".into()); }
    }
    let bytes = serde_json::to_vec(&json!({"schema":"tavix.studio.assets-source/v1","root":root.to_string_lossy()}))
        .map_err(|_| "Cannot encode Assets preference")?;
    if bytes.len() > 4096 { return Err("Assets preference too large".into()); }
    let temp = target.with_extension("json.new");
    if temp.exists() { return Err("Assets preference update already pending".into()); }
    fs::write(&temp, bytes).map_err(|_| "Cannot save Assets preference")?;
    if target.exists() { fs::remove_file(&target).map_err(|_| "Cannot update Assets preference")?; }
    fs::rename(temp, target).map_err(|_| "Cannot finalize Assets preference")?;
    // No local path returns to the frontend.
    Ok(json!({"connected":true,"source":"operator"}))
}

#[tauri::command]
pub(crate) fn studio_reset_assets() -> Result<Value, String> {
    let file = preference_path()?;
    if file.exists() {
        let meta = file.symlink_metadata().map_err(|_| "Assets preference unavailable")?;
        if !meta.is_file() || meta.file_type().is_symlink() { return Err("Unsafe Assets preference".into()); }
        fs::remove_file(file).map_err(|_| "Cannot reset Assets preference")?;
    }
    Ok(json!({"reset":true}))
}
