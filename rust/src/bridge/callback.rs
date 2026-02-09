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
    let fut = Python::with_gil(|py| -> PyResult<_> {
        let handler = handler.as_ref().clone_ref(py);
        let ctx = request_to_py_context(py, &request)?;
        let coroutine = handler.bind(py).call1((ctx,))?;
        pyo3_async_runtimes::tokio::into_future(coroutine)
    })?;

    let py_obj = fut.await.map_err(CoreError::from)?;
    Python::with_gil(|py| py_to_response(py, py_obj.into_bound(py)))
}
