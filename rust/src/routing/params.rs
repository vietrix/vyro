use std::collections::HashMap;
use std::sync::Arc;

use pyo3::prelude::*;

pub struct LookupResult {
    pub handler: Arc<Py<PyAny>>,
    pub path_params: HashMap<String, String>,
}
