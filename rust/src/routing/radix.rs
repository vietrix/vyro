use std::sync::Arc;

use pyo3::prelude::*;

#[derive(Clone)]
pub struct RouteHandler {
    pub handler: Arc<Py<PyAny>>,
}

pub struct RouteDefinition {
    pub method: String,
    pub path: String,
    pub handler: Py<PyAny>,
}
