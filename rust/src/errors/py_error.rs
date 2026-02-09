use pyo3::exceptions::PyRuntimeError;
use pyo3::PyErr;

use crate::errors::core_error::CoreError;

pub fn to_py_runtime(err: CoreError) -> PyErr {
    PyRuntimeError::new_err(err.to_string())
}
