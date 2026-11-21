//! Operator-local catalog publication plans. These are *not* LoopRD store offers
//! or authority to price, list, install, publish, or grant an entitlement.
use serde_json::{json, Value};
use std::{fs, io::Write, path::PathBuf};

const SCHEMA: &str = "tavix.studio.catalog-drafts/v1";
const MAX_DRAFT_BYTES: u64 = 512 * 1024;
const MAX_ROWS: usize = 400;

fn draft_path() -> Result<PathBuf, String> {
    Ok(super::review::state_root()?.join("catalog-drafts.json"))
}

fn valid_row(key: &str) -> Result<(), String> {
    if let Some(digest) = key.strip_prefix("submission:") {
        if digest.len() != 64 || !digest.bytes().all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c)) {
            return Err("CATALOG_ROW_INVALID: Invalid exact package identity".into());
        }
        // Never accept an invented submission or a key provided as an OS path.
        let path = super::review::state_root()?.join("reviews").join(format!("{digest}.json"));
        let meta = path.symlink_metadata().map_err(|_| "CATALOG_ROW_UNKNOWN: Local review missing")?;
        if !meta.is_file() || meta.file_type().is_symlink() || meta.len() > 100_000 {
            return Err("CATALOG_ROW_UNKNOWN: Unsafe local review".into());
        }
        let review: Value = serde_json::from_slice(&fs::read(path).map_err(|_| "CATALOG_ROW_UNKNOWN")?)
            .map_err(|_| "CATALOG_ROW_UNKNOWN: Invalid review")?;
        if review.get("sha256").and_then(Value::as_str) != Some(digest) {
            return Err("CATALOG_ROW_UNKNOWN: Review identity mismatch".into());
        }
        // Neither legacy/stale records nor designer data may become offers.
        if !matches!(review.get("kind").and_then(Value::as_str), Some("tavix") | Some("tavia")) {
            return Err("CATALOG_ROW_NOT_SELLABLE: Only apps and asset packs are merchandise".into());
        }
        return Ok(());
    }
    if key.starts_with("blueprint:") {
        // Legacy draft keys are intentionally preserved on disk but cannot be
        // modified or published: a TAVIB only describes asset compatibility.
        return Err("CATALOG_ROW_NOT_SELLABLE: Blueprints are not store products".into());
    }
    Err("CATALOG_ROW_INVALID: Only local application and asset-pack submissions can be edited".into())
}

fn load() -> Result<Value, String> {
    let path = draft_path()?;
    if !path.exists() {return Ok(json!({"schema":SCHEMA,"entries":{}}));}
    let meta = path.symlink_metadata().map_err(|_| "Cannot inspect publication plans")?;
    if !meta.is_file() || meta.file_type().is_symlink() || meta.len() > MAX_DRAFT_BYTES {
        return Err("CATALOG_DRAFT_UNSAFE: Operator draft file is not safe to open".into());
    }
    let record:Value = serde_json::from_slice(&fs::read(&path).map_err(|_| "Cannot read publication plans")?)
        .map_err(|_| "CATALOG_DRAFT_INVALID: Invalid local plan JSON")?;
    if record.get("schema").and_then(Value::as_str) != Some(SCHEMA)
       || !record.get("entries").and_then(Value::as_object).map(|e|e.len()<=MAX_ROWS).unwrap_or(false) {
        return Err("CATALOG_DRAFT_INVALID: Unsupported local publication plan".into());
    }
    Ok(record)
}

#[tauri::command]
pub(crate) fn studio_catalog_drafts() -> Result<Value, String> {
    // Preserve any historical blueprint draft bytes in the operator profile,
    // but never return them to the commercial Publishing editor.
    let mut record = load()?;
    if let Some(entries) = record.get_mut("entries").and_then(Value::as_object_mut) {
        entries.retain(|key, _| !key.starts_with("blueprint:"));
    }
    Ok(record)
}

#[tauri::command]
pub(crate) fn studio_catalog_save_draft(
    row_key:String, price_gold:Option<u32>, listed:bool, testing:bool, summary:String
) -> Result<Value, String> {
    valid_row(&row_key)?;
    if price_gold.map(|p|p>1_000_000).unwrap_or(false) || summary.chars().count()>240
       || summary.chars().any(|c|c.is_control() && c!='\n') {
        return Err("CATALOG_DRAFT_INVALID: Invalid price or description".into());
    }
    let mut draft=load()?;
    let entries=draft.get_mut("entries").and_then(Value::as_object_mut)
        .ok_or("CATALOG_DRAFT_INVALID")?;
    if entries.len()>=MAX_ROWS && !entries.contains_key(&row_key) {
        return Err("CATALOG_DRAFT_FULL: Too many local publication plans".into());
    }
    let row=json!({"priceGold":price_gold,"listed":listed,"testing":testing,
       "summary":summary,"publicationAuthorized":false,"remoteApplied":false});
    // Retain the exact identity for the response after inserting the saved draft.
    // HashMap/serde_json::Map::insert takes ownership of its key.
    entries.insert(row_key.clone(),row.clone());
    let bytes=serde_json::to_vec_pretty(&draft).map_err(|_| "Cannot encode publication plans")?;
    if bytes.len() as u64>MAX_DRAFT_BYTES {return Err("CATALOG_DRAFT_FULL: Local plans exceed size limit".into());}
    let path=draft_path()?;
    let pending=path.with_extension("json.new");
    if pending.exists() {return Err("CATALOG_DRAFT_PENDING: Pending operator file requires inspection".into());}
    let mut f=fs::OpenOptions::new().write(true).create_new(true).open(&pending)
        .map_err(|_| "Cannot stage publication plan")?;
    if f.write_all(&bytes).and_then(|_|f.sync_all()).is_err() {
        let _=fs::remove_file(&pending);
        return Err("Cannot write publication plan".into());
    }
    drop(f);
    // Windows does not allow renaming over an existing file. Follow the same
    // source-owned private-profile update convention as the review subsystem.
    if path.exists() {
        let meta=path.symlink_metadata().map_err(|_| "Cannot replace publication plan")?;
        if !meta.is_file() || meta.file_type().is_symlink() {return Err("CATALOG_DRAFT_UNSAFE".into());}
        fs::remove_file(&path).map_err(|_| "Cannot replace publication plan")?;
    }
    fs::rename(&pending,&path).map_err(|_| "Cannot commit publication plan".to_string())?;
    Ok(json!({"schema":SCHEMA,"rowKey":row_key,"draft":row,"remoteApplied":false}))
}
