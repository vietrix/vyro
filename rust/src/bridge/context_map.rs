use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBytes, PyDict};

use crate::http::request::IncomingRequest;

pub const CONTEXT_HEADERS_KEY: &str = "headers";
pub const CONTEXT_QUERY_KEY: &str = "query";
pub const CONTEXT_PATH_PARAMS_KEY: &str = "path_params";
pub const CONTEXT_BODY_KEY: &str = "body";

pub fn request_to_py_context(py: Python<'_>, req: &IncomingRequest) -> PyResult<Py<PyAny>> {
    let payload = PyDict::new(py);
    payload.set_item(CONTEXT_HEADERS_KEY, &req.headers)?;
    payload.set_item(CONTEXT_QUERY_KEY, &req.query)?;
    payload.set_item(CONTEXT_PATH_PARAMS_KEY, &req.path_params)?;
    payload.set_item(CONTEXT_BODY_KEY, PyBytes::new(py, &req.body))?;
    Ok(payload.into_any().unbind())
}
