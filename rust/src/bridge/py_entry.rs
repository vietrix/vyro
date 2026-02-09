use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::bridge::route_map::parse_routes;
use crate::errors::py_error::to_py_runtime;
use crate::lifecycle::runtime::run;

#[pyfunction]
pub fn start_server(
    py: Python<'_>,
    host: String,
    port: u16,
    workers: usize,
    routes: Bound<'_, PyAny>,
) -> PyResult<()> {
    if host.trim().is_empty() {
        return Err(PyValueError::new_err("host cannot be empty"));
    }
    let routes = parse_routes(&routes)?;
    let workers = workers.max(1);
    py.allow_threads(move || run(host, port, workers, routes))
        .map_err(to_py_runtime)
}
