use std::collections::HashMap;

use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBytes, PyDict, PyList, PyString, PyTuple};

use crate::errors::core_error::CoreError;
use crate::http::response::OutgoingResponse;
use crate::serialization::json::to_json_bytes;

pub fn py_to_response(
    py: Python<'_>,
    obj: Bound<'_, PyAny>,
) -> Result<OutgoingResponse, CoreError> {
    if let Ok(tuple) = obj.downcast::<PyTuple>() {
        return tuple_to_response(py, tuple);
    }

    let (body, content_type) = py_to_body(py, &obj)?;
    let mut headers = HashMap::new();
    if let Some(ct) = content_type {
        headers.insert("content-type".to_string(), ct);
    }
    Ok(OutgoingResponse {
        status: 200,
        headers,
        body,
    })
}

fn tuple_to_response(
    py: Python<'_>,
    tuple: &Bound<'_, PyTuple>,
) -> Result<OutgoingResponse, CoreError> {
    if tuple.len() != 2 && tuple.len() != 3 {
        return Err(CoreError::ResponseBuild(
            "tuple response must be (body, status) or (body, status, headers)".to_string(),
        ));
    }
    let body_obj = tuple.get_item(0).map_err(CoreError::from)?;
    let status: u16 = tuple
        .get_item(1)
        .map_err(CoreError::from)?
        .extract()
        .map_err(CoreError::from)?;
    let mut headers = HashMap::new();
    if tuple.len() == 3 {
        let headers_obj = tuple.get_item(2).map_err(CoreError::from)?;
        if let Ok(dict) = headers_obj.downcast::<PyDict>() {
            for (k, v) in dict.iter() {
                let key: String = k.extract().map_err(CoreError::from)?;
                let value: String = v.extract().map_err(CoreError::from)?;
                headers.insert(key.to_ascii_lowercase(), value);
            }
        } else {
            return Err(CoreError::ResponseBuild(
                "headers must be a dict[str, str]".to_string(),
            ));
        }
    }

    let (body, content_type) = py_to_body(py, &body_obj)?;
    if let Some(ct) = content_type {
        headers.entry("content-type".to_string()).or_insert(ct);
    }
    Ok(OutgoingResponse {
        status,
        headers,
        body,
    })
}

fn py_to_body(
    py: Python<'_>,
    obj: &Bound<'_, PyAny>,
) -> Result<(Vec<u8>, Option<String>), CoreError> {
    if obj.is_none() {
        return Ok((
            Vec::new(),
            Some("application/json; charset=utf-8".to_string()),
        ));
    }
    if let Ok(bytes) = obj.downcast::<PyBytes>() {
        return Ok((bytes.as_bytes().to_vec(), None));
    }
    if let Ok(text) = obj.downcast::<PyString>() {
        let s = text.to_string();
        return Ok((
            s.into_bytes(),
            Some("text/plain; charset=utf-8".to_string()),
        ));
    }
    if obj.is_instance_of::<PyDict>() || obj.is_instance_of::<PyList>() {
        let body = to_json_bytes(py, obj)?;
        return Ok((body, Some("application/json; charset=utf-8".to_string())));
    }
    let body = to_json_bytes(py, obj)?;
    Ok((body, Some("application/json; charset=utf-8".to_string())))
}
