//! Native TaviX Studio boundary: bounded read APIs and explicit operator review only.
//! No TAVIA archive parser is copied here: the canonical Tavi Assets validator remains authoritative.
mod review;
mod studio_connection;
mod studio_catalog;
mod studio_publish;
use serde::Serialize;
use serde_json::Value;
use std::{fs, path::Path, process::Command};

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct PackageSummary {
    id: String,
    name: String,
    version: String,
    classification: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct WorkspaceSnapshot {
    tool_version: String,
    git_commit: String,
    git_dirty: bool,
    assets_checkout_detected: bool,
    packages: Vec<PackageSummary>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct EventSummary {
    id: String,
    level: String,
    code: String,
    timestamp: String,
}

fn valid_checkout(candidate: &Path) -> Option<std::path::PathBuf> {
    let root = candidate.canonicalize().ok()?;
    let metadata = root.join("project.zr").symlink_metadata().ok()?;
    if !metadata.is_file() || metadata.file_type().is_symlink() || metadata.len() > 65536 {
        return None;
    }
    let config: Value = serde_json::from_slice(&fs::read(root.join("project.zr")).ok()?).ok()?;
    (config.get("project_key").and_then(Value::as_str) == Some("tavix")).then_some(root)
}

fn root_dir() -> Option<std::path::PathBuf> {
    // Environment is trusted operator process configuration, never a renderer argument.
    if let Some(path) = std::env::var_os("TAVIX_REPO_ROOT") {
        return valid_checkout(Path::new(&path));
    }
    if let Ok(cwd) = std::env::current_dir() {
        for candidate in cwd.ancestors().take(8) {
            if let Some(root) = valid_checkout(candidate) { return Some(root); }
        }
    }
    // Compile-time source-tree fallback for developers, not a portable installed-app location.
    valid_checkout(&Path::new(env!("CARGO_MANIFEST_DIR")).join("../../.."))
}

fn safe_text(value: &Value, key: &str, max: usize) -> String {
    value.get(key).and_then(Value::as_str).unwrap_or("")
        .chars().filter(|c| !c.is_control()).take(max).collect()
}

fn git_read(root: &Path, args: &[&str]) -> Option<String> {
    let mut command=Command::new("git");
    command.args(args).current_dir(root);
    #[cfg(windows)] {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    let output=command.output().ok()?;
    if !output.status.success() { return None }
    let text = String::from_utf8(output.stdout).ok()?;
    Some(text.trim().chars().take(160).collect())
}

fn packages(root: &Path) -> Vec<PackageSummary> {
    let mut results = Vec::new();
    let Ok(apps) = fs::read_dir(root.join("extensions")) else { return results };
    for app in apps.flatten().take(100) {
        if !app.file_type().map(|t| t.is_dir() && !t.is_symlink()).unwrap_or(false) { continue }
        let Ok(versions) = fs::read_dir(app.path()) else { continue };
        for version in versions.flatten().take(50) {
            if !version.file_type().map(|t| t.is_dir() && !t.is_symlink()).unwrap_or(false) { continue }
            let path = version.path().join("manifest.json");
            if !path.symlink_metadata().map(|m| m.is_file() && !m.file_type().is_symlink() && m.len() <= 131072).unwrap_or(false) { continue }
            let Ok(data) = fs::read(path) else { continue };
            let Ok(manifest) = serde_json::from_slice::<Value>(&data) else { continue };
            let id = safe_text(&manifest, "id", 120);
            let ver = safe_text(&manifest, "version", 40);
            if id.is_empty() || ver.is_empty() { continue }
            let kind = manifest.pointer("/classification/type").and_then(Value::as_str).unwrap_or("app");
            results.push(PackageSummary {
                id, version: ver, name: safe_text(&manifest, "name", 120),
                classification: if kind == "game" { "game" } else { "app" }.to_owned(),
            });
            if results.len() >= 250 { return results }
        }
    }
    results.sort_by(|a, b| a.name.cmp(&b.name).then(a.version.cmp(&b.version)));
    results
}

#[tauri::command]
fn workspace_snapshot() -> Result<WorkspaceSnapshot, String> {
    let root = root_dir().ok_or_else(|| "TaviX checkout unavailable; set TAVIX_REPO_ROOT".to_string())?;
    let raw = fs::read(root.join("project.zr")).map_err(|_| "TaviX checkout unavailable".to_string())?;
    let cfg: Value = serde_json::from_slice(&raw).map_err(|_| "Invalid project metadata".to_string())?;
    if cfg.get("project_key").and_then(Value::as_str) != Some("tavix") {
        return Err("Selected checkout is not TaviX".into());
    }
    let commit = git_read(&root, &["rev-parse", "--short", "HEAD"]).unwrap_or_else(|| "not linked".into());
    let dirty = git_read(&root, &["status", "--porcelain=v1", "-uno"]).map(|s| !s.is_empty()).unwrap_or(false);
    let assets_root = root.join("../tavi-assets");
    Ok(WorkspaceSnapshot {
        tool_version: safe_text(&cfg, "version", 32), git_commit: commit, git_dirty: dirty,
        assets_checkout_detected: assets_root.join("project.zr").is_file(),
        packages: packages(&root),
    })
}

#[tauri::command]
fn recent_events() -> Vec<EventSummary> {
    // Diagnostics are the existing TaviX journal, but do not expose its free-text messages.
    let Some(home) = std::env::var_os(if cfg!(windows) { "USERPROFILE" } else { "HOME" }) else { return vec![] };
    let path = Path::new(&home).join(".tavix-suite/events.jsonl");
    let Ok(meta) = path.symlink_metadata() else { return vec![] };
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len() > 524288 { return vec![] }
    let Ok(raw) = fs::read_to_string(path) else { return vec![] };
    raw.lines().rev().take(30).filter_map(|line| {
        let event = serde_json::from_str::<Value>(line).ok()?;
        Some(EventSummary {
            id: safe_text(&event, "id", 48),
            level: safe_text(&event, "level", 16),
            code: safe_text(&event, "code", 80),
            timestamp: safe_text(&event, "at", 40),
        })
    }).filter(|event| !event.id.is_empty()).collect()
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![workspace_snapshot, recent_events, review::review_blueprints, review::review_import_blueprint, review::review_discover_tavib, review::review_tavib_detail, review::review_commit_tavib, review::review_submissions, review::review_import, review::review_recheck, review::review_decide, review::review_export, studio_connection::studio_health, studio_connection::studio_connect_assets, studio_connection::studio_reset_assets, review::review_catalog, review::review_preview, studio_publish::studio_publishing_targets, studio_publish::studio_save_publishing_targets, studio_publish::studio_probe_publishing_targets, studio_publish::studio_github_releases, studio_publish::studio_github_auth, studio_publish::studio_github_login, studio_publish::studio_github_catalog_sync, studio_publish::studio_github_catalog_preview, studio_publish::studio_github_catalog_prepare, studio_publish::studio_github_create_draft, studio_publish::studio_github_publish_draft, studio_publish::studio_github_release_receipt, studio_publish::studio_looprd_connect, studio_publish::studio_looprd_catalog, studio_publish::studio_looprd_inspect, studio_publish::studio_looprd_stage, studio_publish::studio_looprd_publish, studio_catalog::studio_catalog_drafts, studio_catalog::studio_catalog_save_draft])
        .run(tauri::generate_context!())
        .expect("TaviX Studio failed to initialize");
}
