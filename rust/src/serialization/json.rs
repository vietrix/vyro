use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};

use crate::errors::core_error::CoreError;

pub fn to_json_bytes(py: Python<'_>, obj: &Bound<'_, PyAny>) -> Result<Vec<u8>, CoreError> {
    let json = py.import("json").map_err(CoreError::from)?;
    let dumped = json
        .call_method1("dumps", (obj,))
        .map_err(CoreError::from)?;

    if let Ok(s) = dumped.downcast::<PyString>() {
        let txt = s.to_string();
        #[cfg(feature = "simd-json")]
        {
            let mut value: serde_json::Value = serde_json::from_str(&txt)
                .map_err(|e| CoreError::ResponseBuild(format!("json parse error: {e}")))?;
            let mut out = Vec::new();
            simd_json::to_writer(&mut out, &mut value).map_err(|e| {
                CoreError::ResponseBuild(format!("simd-json serialization error: {e}"))
            })?;
            return Ok(out);
        }
        #[cfg(not(feature = "simd-json"))]
        {
            return Ok(txt.into_bytes());
        }
    }

    if let Ok(b) = dumped.downcast::<PyBytes>() {
        return Ok(b.as_bytes().to_vec());
    }

    Err(CoreError::ResponseBuild(
        "json.dumps returned unsupported type".to_string(),
    ))
}
