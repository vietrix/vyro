use crate::errors::core_error::CoreError;
use crate::http::server::serve;
use crate::lifecycle::bootstrap::build_runtime;
use crate::routing::method_table::RouteRegistry;
use crate::routing::radix::RouteDefinition;

pub fn run(
    host: String,
    port: u16,
    workers: usize,
    routes: Vec<RouteDefinition>,
) -> Result<(), CoreError> {
    let runtime = build_runtime(workers)?;
    let registry = RouteRegistry::from_routes(routes)?;
    runtime.block_on(serve(host, port, registry))
}
