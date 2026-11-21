//! Native Studio operator review. Package bytes never enter the renderer.
//! Canonical validation and review-ZIP creation are delegated to a fixed local
//! Python source tool, not to a privileged browser/extension or local HTTP host.
use serde_json::{json, Value};
use std::{fs, io::Write, path::PathBuf, process::Command};

const MAX_PACKAGE: u64 = 48 * 1024 * 1024;
const MAX_NOTE: usize = 2000;

pub(crate) fn state_root() -> Result<PathBuf, String> {
    let base = std::env::var_os(if cfg!(windows) { "LOCALAPPDATA" } else { "HOME" })
        .ok_or("Local operator profile unavailable")?;
    let path = if cfg!(windows) { PathBuf::from(base).join("TaviXStudio") }
               else { PathBuf::from(base).join(".local/share/tavix-studio") };
    fs::create_dir_all(path.join("submissions")).map_err(|_| "Cannot initialize review storage")?;
    fs::create_dir_all(path.join("reviews")).map_err(|_| "Cannot initialize review storage")?;
    // Refuse symlinked review directories; do not follow a redirected private root.
    for member in [path.clone(), path.join("submissions"), path.join("reviews")] {
        if member.symlink_metadata().map_err(|_| "Review storage unavailable")?.file_type().is_symlink() {
            return Err("Linked review storage is not permitted".into());
        }
    }
    Ok(path)
}

pub(crate) fn script_call(action: &str, args: &[String]) -> Result<Value, String> {
    let root = super::root_dir().ok_or("TaviX checkout unavailable")?;
    let tool = root.join("tools/studio-desktop/review_cli.py");
    if !tool.is_file() || tool.symlink_metadata().map_err(|_| "Review tool unavailable")?.file_type().is_symlink() {
        return Err("Trusted Studio review tool unavailable".into());
    }
    let mut command = Command::new("python");
    command.arg("-I").arg(&tool).arg(action).arg(&root).args(args)
        .current_dir(&root);
    // CREATE_NO_WINDOW: Python validators must never create transient console
    // windows on Windows (including nested import operations).
    #[cfg(windows)] {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    let output = command.output().map_err(|_| "STUDIO_PYTHON_UNAVAILABLE: Cannot launch Python. Check Python is available to the Studio process")?;
    if output.stdout.len() > 256 * 1024 {
        return Err("Validator response exceeds safe limit".into());
    }
    // Fail with safe, stable codes when Python exits without the JSON envelope.
    // No stderr is sent to the renderer: it may contain full paths and private data.
    if output.stdout.is_empty() {
        return Err("STUDIO_VALIDATOR_NO_RESPONSE: Python returned no JSON. Check the installed source version and the Studio Events diagnostic report".into());
    }
    let data: Value = serde_json::from_slice(&output.stdout)
        .map_err(|_| "STUDIO_VALIDATOR_PROTOCOL: Python returned a non-JSON response. Confirm the Studio executable matches this checkout")?;
    if !output.status.success() || data.get("ok") != Some(&Value::Bool(true)) {
        let code = data.get("code").and_then(Value::as_str).unwrap_or("REVIEW_REJECTED");
        let reason = data.get("reason").and_then(Value::as_str).unwrap_or("Package review was rejected");
        // Only accept bounded, machine-safe reason codes. No subprocess stderr or user paths.
        let safe_code = if code.len() <= 48 && code.bytes().all(|c| c.is_ascii_uppercase() || c == b'_' || c.is_ascii_digit()) { code } else { "REVIEW_REJECTED" };
        return Err(format!("{safe_code}: {}", reason.chars().take(220).collect::<String>()));
    }
    data.get("result").cloned().ok_or("Missing review result".into())
}

fn safe_id(id: &str) -> bool {
    id.len() == 64 && id.bytes().all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
}

fn review_path(id: &str) -> Result<PathBuf, String> {
    if !safe_id(id) { return Err("Invalid review ID".into()); }
    Ok(state_root()?.join("reviews").join(format!("{id}.json")))
}

fn read_review(id: &str) -> Result<Value, String> {
    let path = review_path(id)?;
    let meta = path.symlink_metadata().map_err(|_| "Review not found")?;
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len() > 100_000 {
        return Err("Unsafe review record".into());
    }
    let result: Value = serde_json::from_slice(&fs::read(path).map_err(|_| "Review unavailable")?)
        .map_err(|_| "Review record is invalid")?;
    if result.get("sha256").and_then(Value::as_str) != Some(id) {
        return Err("Review identity mismatch".into());
    }
    Ok(result)
}

fn save_review(id: &str, record: &Value) -> Result<(), String> {
    let path = review_path(id)?;
    let bytes = serde_json::to_vec_pretty(record).map_err(|_| "Review serialization failed")?;
    if bytes.len() > 100_000 { return Err("Review record too large".into()); }
    let tmp = path.with_extension("json.new");
    let mut file = fs::OpenOptions::new().create_new(true).write(true).open(&tmp)
        .map_err(|_| "Cannot stage review update")?;
    file.write_all(&bytes).map_err(|_| "Cannot write review update")?;
    file.sync_all().map_err(|_| "Cannot save review update")?;
    drop(file);
    if path.exists() { fs::remove_file(&path).map_err(|_| "Cannot update review")?; }
    fs::rename(&tmp, &path).map_err(|_| "Cannot finalize review update".to_string())
}

fn submitted_path(report: &Value) -> Result<PathBuf, String> {
    let id = report.get("sha256").and_then(Value::as_str).ok_or("Missing digest")?;
    let format = report.get("kind").and_then(Value::as_str).ok_or("Missing package format")?;
    if !safe_id(id) || !["tavix", "tavia"].contains(&format) { return Err("Invalid package identity".into()); }
    Ok(state_root()?.join("submissions").join(format!("{id}.{format}")))
}

fn blueprint_summary(item: &Value, origin: &str, digest_prefix: &str) -> Option<Value> {
    if item.get("schema").and_then(Value::as_str) != Some("tavix.studio.asset-blueprint/v1") { return None; }
    let id = item.get("id")?.as_str()?;
    if !id.chars().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c=='-')
        || id.is_empty() || id.len()>71 || (origin=="operator" && !id.starts_with("local-")) { return None; }
    if !item.get("title")?.as_str().map(|v| !v.trim().is_empty() && v.len()<=160).unwrap_or(false)
        || !item.get("description")?.as_str().map(|v| v.len()<=1200).unwrap_or(false)
        || !item.get("version")?.as_str().map(|v| v.len()<=32).unwrap_or(false)
        || !item.get("applicablePackTypes")?.as_array().map(|v| !v.is_empty() && v.len()<=32 && v.iter().all(Value::is_string)).unwrap_or(false)
        || !item.get("designerChecklist")?.as_array().map(|v| !v.is_empty() && v.len()<=64 && v.iter().all(Value::is_string)).unwrap_or(false) {return None;}
    let required = item.get("requiredResources")?.as_array()?.len();
    let prefixes: usize = item.get("requiredPrefixes").and_then(Value::as_object)
        .map_or(0, |map| map.values().filter_map(Value::as_u64).fold(0usize,|n,v| n.saturating_add(v.min(1281) as usize)));
    if required+prefixes==0 || required+prefixes>1280
        || !item.get("requiredResources")?.as_array()?.iter().all(Value::is_string)
        || !item.get("requiredPrefixes").map(|v|v.is_object()).unwrap_or(true) {return None;}
    Some(json!({
        "id": id, "title": item.get("title")?, "version":item.get("version")?,
        "description": item.get("description")?,
        "applicablePackTypes":item.get("applicablePackTypes")?,
        "requiredCount":required+prefixes,
        "designerChecklist":item.get("designerChecklist")?,
        "requiredResources":item.get("requiredResources")?,
        "requiredPrefixes":item.get("requiredPrefixes").cloned().unwrap_or(json!({})),
        "origin":origin,"digestPrefix":digest_prefix,
    }))
}

#[tauri::command]
pub(crate) fn review_blueprints() -> Result<Value, String> {
    // Built-ins are embedded, independent of Python availability. Operator-local
    // imports are data-only, validated again by the canonical review CLI on use.
    const BUNDLED: [&str; 4] = [
        include_str!("../../blueprints/cards-back-only.json"),
        include_str!("../../blueprints/cards-standard-54.json"),
        include_str!("../../blueprints/dice-d6-2d.json"),
        include_str!("../../blueprints/tarot-standard-78.json"),
    ];
    let mut result=Vec::new();
    for source in BUNDLED {
        let item: Value=serde_json::from_str(source).map_err(|_| "Bundled asset blueprint is malformed".to_string())?;
        result.push(blueprint_summary(&item,"bundled","").ok_or("Bundled asset blueprint has an unsupported schema")?);
    }
    let dir=state_root()?.join("blueprints");
    if dir.exists() {
        let meta=dir.symlink_metadata().map_err(|_| "Operator blueprint directory unavailable")?;
        if !meta.is_dir() || meta.file_type().is_symlink() { return Err("Unsafe operator blueprint directory".into()); }
        for file in fs::read_dir(dir).map_err(|_| "Cannot read operator blueprints")?.flatten().take(100) {
            let path=file.path();
            let Some(name)=path.file_stem().and_then(|s|s.to_str()) else {continue};
            if !name.starts_with("local-") || path.extension().and_then(|s|s.to_str())!=Some("json") {continue;}
            if !file.metadata().map(|m|m.is_file() && m.len()>0 && m.len()<=32768).unwrap_or(false)
                || path.symlink_metadata().map(|m|m.file_type().is_symlink()).unwrap_or(true) {continue;}
            let Ok(bytes)=fs::read(&path) else {continue};
            let Ok(item)=serde_json::from_slice::<Value>(&bytes) else {continue};
            if item.get("id").and_then(Value::as_str)!=Some(name) {continue;}
            if let Some(mut summary)=blueprint_summary(&item,"operator","") {
                if name.starts_with("local-app-") {
                    let origin=state_root()?.join("blueprints/.origins").join(format!("{name}.json"));
                    if let Ok(meta)=origin.symlink_metadata() {
                        if meta.is_file() && !meta.file_type().is_symlink() && meta.len()<=4096 {
                            if let Ok(raw)=fs::read(origin) {if let Ok(value)=serde_json::from_slice::<Value>(&raw) {
                                if value.get("schema").and_then(Value::as_str)==Some("tavix.studio.embedded-blueprint-origin/v1") {
                                    summary["origin"]=json!("app");
                                    summary["sourceApp"]=value.get("appId").cloned().unwrap_or(json!(""));
                                    summary["sourceAppVersion"]=value.get("appVersion").cloned().unwrap_or(json!(""));
                                    summary["upstreamId"]=value.get("upstreamId").cloned().unwrap_or(json!(""));
                                    summary["digestPrefix"]=json!(value.get("tavibDigest").and_then(Value::as_str).unwrap_or("").chars().take(12).collect::<String>());
                                }
                            }}
                        }
                    }
                }
                result.push(summary);
            }
        }
    }
    result.sort_by(|a,b| a.get("title").and_then(Value::as_str).cmp(&b.get("title").and_then(Value::as_str)));
    Ok(Value::Array(result))
}

#[tauri::command]
pub(crate) fn review_import_blueprint() -> Result<Value,String> {
    let source=rfd::FileDialog::new().add_filter("Designer blueprint JSON", &["json"])
        .pick_file().ok_or("Blueprint import cancelled")?;
    let meta=source.symlink_metadata().map_err(|_| "Blueprint file unavailable")?;
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len()==0 || meta.len()>32768
        || source.extension().and_then(|s|s.to_str())!=Some("json") {
        return Err("BLUEPRINT_FILE_INVALID: Choose a JSON blueprint of at most 32 KiB".into());
    }
    // The file path is supplied ONLY by the trusted native picker, not the webview.
    script_call("blueprint_import", &[source.to_string_lossy().to_string()])
}

#[tauri::command]
pub(crate) fn review_discover_tavib() -> Result<Value,String> {
    let path=rfd::FileDialog::new().add_filter("TaviX app with blueprints", &["tavix"])
        .pick_file().ok_or("Blueprint application selection cancelled")?;
    let meta=path.symlink_metadata().map_err(|_| "TAVIB_PACKAGE_UNAVAILABLE")?;
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len()==0 || meta.len()>MAX_PACKAGE {
        return Err("TAVIB_PACKAGE_UNAVAILABLE: Choose a bounded local TaviX application".into());
    }
    let candidate=script_call("tavib_discover", &[path.to_string_lossy().to_string()])?;
    let digest=candidate.get("digest").and_then(Value::as_str).ok_or("Missing application digest")?;
    if !safe_id(digest) {return Err("Invalid application digest".into());}
    let folder=state_root()?.join("blueprint-imports");
    fs::create_dir_all(&folder).map_err(|_| "Cannot prepare blueprint intake")?;
    if folder.symlink_metadata().map_err(|_| "Unsafe blueprint intake")?.file_type().is_symlink() {
        return Err("Unsafe blueprint intake".into());
    }
    let dest=folder.join(format!("{digest}.tavix"));
    if !dest.exists() {
        fs::copy(path,&dest).map_err(|_| "Cannot retain application for blueprint selection")?;
    }
    // The retained bytes MUST independently pass the exact same package checks.
    let checked=script_call("tavib_discover", &[dest.to_string_lossy().to_string()])?;
    if checked.get("digest").and_then(Value::as_str)!=Some(digest) {
        return Err("TAVIB_SOURCE_CHANGED: Retained application changed".into());
    }
    Ok(checked)
}

#[tauri::command]
pub(crate) fn review_tavib_detail(digest:String, member:String) -> Result<Value,String> {
    if !safe_id(&digest) || member.len()>100 || !member.starts_with("schematics/") || !member.ends_with(".tavib") {
        return Err("TAVIB_SELECTION_INVALID: Invalid blueprint selection".into());
    }
    let source=state_root()?.join("blueprint-imports").join(format!("{digest}.tavix"));
    if !source.is_file() || source.symlink_metadata().map_err(|_| "Stored application unavailable")?.file_type().is_symlink() {
        return Err("Stored application unavailable".into());
    }
    script_call("tavib_detail", &[source.to_string_lossy().to_string(), digest, member])
}

#[tauri::command]
pub(crate) fn review_commit_tavib(digest:String, members:Vec<String>) -> Result<Value,String> {
    if !safe_id(&digest) || members.is_empty() || members.len()>24 ||
        members.iter().any(|m| m.len()>100 || !m.starts_with("schematics/") || !m.ends_with(".tavib")) {
        return Err("TAVIB_SELECTION_INVALID: Invalid blueprint selection".into());
    }
    let source=state_root()?.join("blueprint-imports").join(format!("{digest}.tavix"));
    if !source.is_file() || source.symlink_metadata().map_err(|_| "Stored application unavailable")?.file_type().is_symlink() {
        return Err("Stored application unavailable".into());
    }
    let selection=serde_json::to_string(&members).map_err(|_| "Invalid blueprint selection")?;
    script_call("tavib_import", &[source.to_string_lossy().to_string(),digest,selection])
}

#[tauri::command]
pub(crate) fn review_submissions() -> Result<Vec<Value>, String> {
    let root = state_root()?;
    let mut results = Vec::new();
    for item in fs::read_dir(root.join("reviews")).map_err(|_| "Reviews cannot be read")?.flatten().take(500) {
        let path = item.path();
        let Some(id) = path.file_stem().and_then(|s| s.to_str()) else { continue; };
        if !safe_id(id) || path.extension().and_then(|s|s.to_str()) != Some("json") { continue; }
        if let Ok(entry) = read_review(id) { results.push(entry); }
    }
    results.sort_by(|a,b| b.get("submittedAt").and_then(Value::as_u64).cmp(&a.get("submittedAt").and_then(Value::as_u64)));
    Ok(results)
}

#[tauri::command]
pub(crate) fn review_import(blueprint_id: String) -> Result<Value, String> {
    // A native file-picker gesture; no filesystem path comes from the renderer.
    let file = rfd::FileDialog::new()
        .add_filter("TaviX / Tavi Assets", &["tavix", "tavia"])
        .pick_file().ok_or("Import cancelled")?;
    let metadata = file.symlink_metadata().map_err(|_| "Package unavailable")?;
    if !metadata.is_file() || metadata.file_type().is_symlink() || metadata.len() > MAX_PACKAGE || metadata.len() == 0 {
        return Err("Package missing, linked or too large".into());
    }
    let kind = file.extension().and_then(|s|s.to_str()).unwrap_or("").to_ascii_lowercase();
    if kind != "tavia" && kind != "tavix" { return Err("Choose a .tavia or .tavix file".into()); }
    let _root = super::root_dir().ok_or("TaviX checkout unavailable")?;
    let assets_root = super::studio_connection::assets_checkout();
    let assets_str = assets_root.as_ref().map(|v| v.to_string_lossy().to_string()).unwrap_or("-".into());
    let selected = if kind == "tavia" { blueprint_id } else { "-".into() };
    let mut report = script_call("inspect", &[file.to_string_lossy().to_string(), assets_str.clone(), selected])?;
    let id = report.get("sha256").and_then(Value::as_str).ok_or("Missing package digest")?.to_owned();
    if !safe_id(&id) { return Err("Invalid digest".into()); }
    if let Ok(existing) = read_review(&id) { return Ok(existing); }
    let private = submitted_path(&report)?;
    // Copy immutable original and verify that the source was not changed during import.
    if !private.exists() {
        let temp = private.with_file_name(format!("{id}.pending.{kind}"));
        fs::copy(&file, &temp).map_err(|_| "Cannot retain review submission")?;
        let verify = script_call("inspect", &[temp.to_string_lossy().to_string(), assets_str.clone(), if kind=="tavia" { report.get("blueprint").and_then(|x|x.get("id")).and_then(Value::as_str).unwrap_or("-").to_owned() } else { "-".into() }])?;
        if verify.get("sha256") != report.get("sha256") {
            let _ = fs::remove_file(&temp);
            return Err("Source package changed during import".into());
        }
        fs::rename(&temp, &private).map_err(|_| "Cannot finalize review submission")?;
    }
    let now = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs();
    report["status"] = json!("draft");
    report["submittedAt"] = json!(now);
    report["reviewerNote"] = json!("");
    save_review(&id, &report)?;
    Ok(report)
}

#[tauri::command]
pub(crate) fn review_recheck(id: String, blueprint_id: String) -> Result<Value, String> {
    let old = read_review(&id)?;
    let package = submitted_path(&old)?;
    let assets = super::studio_connection::assets_checkout();
    let format = old.get("kind").and_then(Value::as_str).unwrap_or("");
    let selected = if format == "tavia" { blueprint_id } else { "-".to_owned() };
    let mut updated = script_call("inspect", &[package.to_string_lossy().to_string(),
        assets.as_ref().map(|v| v.to_string_lossy().to_string()).unwrap_or("-".into()),selected])?;
    if updated.get("sha256").and_then(Value::as_str) != Some(id.as_str()) {
        return Err("Stored package digest mismatch".into());
    }
    updated["submittedAt"] = old.get("submittedAt").cloned().unwrap_or(json!(0));
    updated["reviewerNote"] = old.get("reviewerNote").cloned().unwrap_or(json!(""));
    // Reassessment always invalidates earlier review approvals.
    updated["status"] = json!("draft");
    save_review(&id, &updated)?;
    Ok(updated)
}

#[tauri::command]
pub(crate) fn review_decide(id: String, decision: String, note: String) -> Result<Value, String> {
    if !["changes_requested", "review_approved"].contains(&decision.as_str()) {
        return Err("Unsupported decision".into());
    }
    let mut report = read_review(&id)?;
    if decision == "review_approved" && report.get("storeReady") != Some(&Value::Bool(true)) {
        return Err("Canonical validation and blueprint completeness must pass before review approval".into());
    }
    if note.chars().count() > MAX_NOTE { return Err("Reviewer note is too long".into()); }
    let cleaned: String = note.chars().filter(|c| !c.is_control() || *c == '\n').collect();
    if decision == "changes_requested" && cleaned.trim().is_empty() {
        return Err("Please provide the developer with a reason for requested changes".into());
    }
    report["status"] = json!(decision);
    report["reviewerNote"] = json!(cleaned);
    save_review(&id, &report)?;
    Ok(report)
}

#[tauri::command]
pub(crate) fn review_export(id: String, mode: String) -> Result<Value, String> {
    if !["feedback", "preview", "approval"].contains(&mode.as_str()) {
        return Err("Unsupported export mode".into());
    }
    let report = read_review(&id)?;
    if mode == "approval" && report.get("status").and_then(Value::as_str) != Some("review_approved") {
        return Err("Review approval required".into());
    }
    if mode != "feedback" && report.get("canonicalValid") != Some(&Value::Bool(true)) {
        return Err("Invalid packages cannot receive a developer preview or approval handoff".into());
    }
    let proposed_name = format!("tavix-{}-{}-review.zip", &id[..12], mode);
    let dest = rfd::FileDialog::new()
        .add_filter("Review ZIP", &["zip"])
        .set_file_name(&proposed_name)
        .save_file().ok_or("Export cancelled")?;
    if dest.extension().and_then(|s|s.to_str()) != Some("zip") {
        return Err("Feedback must be saved as a .zip".into());
    }
    let path = submitted_path(&report)?;
    if !path.is_file() || path.symlink_metadata().map_err(|_| "Stored submission missing")?.file_type().is_symlink() {
        return Err("Stored submission unavailable".into());
    }
    script_call("export", &[path.to_string_lossy().to_string(),
        review_path(&id)?.to_string_lossy().to_string(), dest.to_string_lossy().to_string(), mode])
}

// The renderer can only request an opaque stored SHA and a fixed catalog mode;
// it cannot open arbitrary local paths or execute untrusted app code.
#[tauri::command]
pub(crate) fn review_catalog(id:String, section:String, offset:u32) -> Result<Value,String> {
    let record=read_review(&id)?;
    let package=submitted_path(&record)?;
    if !package.is_file() || package.symlink_metadata().map_err(|_| "Package unavailable")?.file_type().is_symlink() {
        return Err("Stored review package unavailable".into());
    }
    script_call("catalog", &[package.to_string_lossy().to_string(), id, section,offset.to_string(),"12".into()])
}

#[tauri::command]
pub(crate) fn review_preview(id:String, member:String) -> Result<Value,String> {
    let record=read_review(&id)?;
    let package=submitted_path(&record)?;
    if !package.is_file() || package.symlink_metadata().map_err(|_| "Package unavailable")?.file_type().is_symlink() {
        return Err("Stored review package unavailable".into());
    }
    script_call("preview", &[package.to_string_lossy().to_string(),id,member])
}
