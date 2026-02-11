use std::sync::Arc;

use pyo3::prelude::*;

use crate::bridge::context_map::request_to_py_context;
use crate::bridge::response_map::py_to_response;
use crate::errors::core_error::CoreError;
use crate::http::request::IncomingRequest;
use crate::http::response::OutgoingResponse;

pub async fn call_python_handler(
    handler: Arc<Py<PyAny>>,
    request: IncomingRequest,
) -> Result<OutgoingResponse, CoreError> {
    let py_obj = Python::with_gil(|py| -> PyResult<_> {
        let handler = handler.as_ref().clone_ref(py);
        let ctx = request_to_py_context(py, &request)?;
        let coroutine = handler.bind(py).call1((ctx,))?;
        let asyncio = py.import("asyncio")?;
        Ok(asyncio.call_method1("run", (coroutine,))?.unbind())
    })?;

    Python::with_gil(|py| py_to_response(py, py_obj.bind(py).clone()))
}
