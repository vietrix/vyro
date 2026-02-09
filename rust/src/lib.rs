mod bridge;
mod errors;
mod http;
mod lifecycle;
mod middleware;
mod routing;
mod serialization;

use bridge::py_entry::start_server;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pymodule]
fn _native(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(start_server, m)?)?;
    Ok(())
}
