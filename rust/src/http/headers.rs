use http::header::{HeaderName, HeaderValue};

use crate::errors::core_error::CoreError;

pub fn header_name(raw: &str) -> Result<HeaderName, CoreError> {
    HeaderName::from_bytes(raw.as_bytes())
        .map_err(|e| CoreError::ResponseBuild(format!("invalid header name: {e}")))
}

pub fn header_value(raw: &str) -> Result<HeaderValue, CoreError> {
    HeaderValue::from_str(raw)
        .map_err(|e| CoreError::ResponseBuild(format!("invalid header value: {e}")))
}
