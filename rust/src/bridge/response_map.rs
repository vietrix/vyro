use std::collections::HashMap;
use std::path::PathBuf;

use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBytes, PyDict, PyList, PyString, PyTuple};

use crate::errors::core_error::CoreError;
use crate::http::response::{OutgoingResponse, ResponseBody};
use crate::serialization::content_type::{APPLICATION_JSON_UTF8, TEXT_PLAIN_UTF8};
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
) -> Result<(ResponseBody, Option<String>), CoreError> {
    if obj.is_none() {
        return Ok((
            ResponseBody::Bytes(Vec::new()),
            Some(APPLICATION_JSON_UTF8.to_string()),
        ));
    }
    if let Some(path) = py_to_file_path(py, obj)? {
        return Ok((ResponseBody::File(path), None));
    }
    if let Ok(bytes) = obj.downcast::<PyBytes>() {
        return Ok((ResponseBody::Bytes(bytes.as_bytes().to_vec()), None));
    }
    if let Ok(text) = obj.downcast::<PyString>() {
        let s = text.to_string();
        return Ok((
            ResponseBody::Bytes(s.into_bytes()),
            Some(TEXT_PLAIN_UTF8.to_string()),
        ));
    }
    if obj.is_instance_of::<PyDict>() || obj.is_instance_of::<PyList>() {
        let body = to_json_bytes(py, obj)?;
        return Ok((
            ResponseBody::Bytes(body),
            Some(APPLICATION_JSON_UTF8.to_string()),
        ));
    }
    let body = to_json_bytes(py, obj)?;
    Ok((
        ResponseBody::Bytes(body),
        Some(APPLICATION_JSON_UTF8.to_string()),
    ))
}

fn py_to_file_path(py: Python<'_>, obj: &Bound<'_, PyAny>) -> Result<Option<PathBuf>, CoreError> {
    if obj.is_instance_of::<PyBytes>() || obj.is_instance_of::<PyString>() {
        return Ok(None);
    }
    let fspath = match obj.call_method0("__fspath__") {
        Ok(v) => v,
        Err(err) => {
            if err.is_instance_of::<pyo3::exceptions::PyAttributeError>(py) {
                return Ok(None);
            }
            return Err(CoreError::from(err));
        }
    };
    let path: String = fspath.extract().map_err(CoreError::from)?;
    Ok(Some(PathBuf::from(path)))
}

#[cfg(test)]
mod tests {
    use super::{py_to_response, ResponseBody};
    use pyo3::prelude::*;
    use pyo3::types::PyModule;

    #[test]
    fn pathlib_body_maps_to_file_response() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let pathlib = PyModule::import(py, "pathlib").expect("pathlib import should succeed");
            let path_obj = pathlib
                .getattr("Path")
                .expect("Path symbol should exist")
                .call1(("README.md",))
                .expect("Path constructor should succeed");
            let response = py_to_response(py, path_obj).expect("response mapping should succeed");
            match response.body {
                ResponseBody::File(path) => assert!(path.ends_with("README.md")),
                ResponseBody::Bytes(_) => panic!("expected file response body"),
            }
        });
    }
}
