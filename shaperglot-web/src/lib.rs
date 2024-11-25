use std::collections::HashMap;

use wasm_bindgen::prelude::*;
extern crate console_error_panic_hook;
use google_fonts_languages::{RegionProto, ScriptProto, REGIONS, SCRIPTS};
use shaperglot::{Checker, Languages};

#[wasm_bindgen]
pub fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

#[wasm_bindgen]
extern "C" {
    // Use `js_namespace` here to bind `console.log(..)` instead of just
    // `log(..)`
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

#[wasm_bindgen]
pub fn scripts() -> Result<String, JsValue> {
    let script_hash: HashMap<String, ScriptProto> = SCRIPTS
        .iter()
        .map(|(id, proto)| (id.to_string(), *proto.clone()))
        .collect();
    serde_json::to_string(&script_hash).map_err(|e| e.to_string().into())
}
#[wasm_bindgen]
pub fn regions() -> Result<String, JsValue> {
    let region_hash: HashMap<String, RegionProto> = REGIONS
        .iter()
        .map(|(id, proto)| (id.to_string(), *proto.clone()))
        .collect();
    serde_json::to_string(&region_hash).map_err(|e| e.to_string().into())
}

#[wasm_bindgen]
pub fn check_font(font_data: &[u8]) -> Result<String, JsValue> {
    let checker = Checker::new(font_data).map_err(|e| e.to_string())?;
    let languages = Languages::new();
    let mut results = vec![];
    for language in languages.iter() {
        let result = checker.check(language);
        if result.is_unknown() {
            continue;
        }
        results.push((
            serde_json::to_value(&language.proto).map_err(|e| e.to_string())?,
            if result.is_success() {
                "supported"
            } else if result.is_nearly_success(5) {
                "nearly-supported"
            } else {
                "unsupported"
            },
            serde_json::to_value(&result).map_err(|e| e.to_string())?,
        ));
    }
    serde_json::to_string(&results).map_err(|e| e.to_string().into())
}
