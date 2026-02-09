use tokio::runtime::{Builder, Runtime};

use crate::errors::core_error::CoreError;

pub fn build_runtime(workers: usize) -> Result<Runtime, CoreError> {
    Builder::new_multi_thread()
        .worker_threads(workers.max(1))
        .enable_all()
        .build()
        .map_err(CoreError::from)
}
