use pyo3::prelude::*;

use vyro_native::routing::method_table::RouteRegistry;
use vyro_native::routing::radix::RouteDefinition;

#[test]
fn route_registry_lookup_normalizes_http_method() {
    Python::with_gil(|py| {
        let routes = vec![RouteDefinition {
            method: "GET".to_string(),
            path: "/users/{id}".to_string(),
            handler: py.None(),
        }];

        let registry = RouteRegistry::from_routes(routes).expect("registry should build");
        let found = registry.lookup("get", "/users/42");
        assert!(found.is_some());
    });
}
