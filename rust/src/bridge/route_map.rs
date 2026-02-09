use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};

use crate::routing::radix::RouteDefinition;

pub fn parse_routes(routes: &Bound<'_, PyAny>) -> PyResult<Vec<RouteDefinition>> {
    let list = routes
        .downcast::<PyList>()
        .map_err(|_| PyValueError::new_err("routes must be a list of tuples"))?;
    let mut out = Vec::with_capacity(list.len());
    for item in list.iter() {
        let tuple = item.downcast::<PyTuple>().map_err(|_| {
            PyValueError::new_err("each route must be tuple(method, path, handler)")
        })?;
        if tuple.len() != 3 {
            return Err(PyValueError::new_err(
                "each route must have exactly 3 items: (method, path, handler)",
            ));
        }
        let method: String = tuple.get_item(0)?.extract()?;
        let path: String = tuple.get_item(1)?.extract()?;
        let handler: Py<PyAny> = tuple.get_item(2)?.extract()?;
        out.push(RouteDefinition {
            method,
            path,
            handler,
        });
    }
    Ok(out)
}
