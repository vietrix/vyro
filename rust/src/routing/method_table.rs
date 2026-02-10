use std::collections::HashMap;
use std::sync::Arc;

use matchit::Router;

use crate::errors::core_error::CoreError;
use crate::routing::errors::RoutingResult;
use crate::routing::params::LookupResult;
use crate::routing::radix::{RouteDefinition, RouteHandler};

#[derive(Clone, Default)]
pub struct RouteRegistry {
    method_routers: HashMap<String, Arc<Router<RouteHandler>>>,
}

impl RouteRegistry {
    pub fn from_routes(routes: Vec<RouteDefinition>) -> RoutingResult<Self> {
        let mut per_method: HashMap<String, Router<RouteHandler>> = HashMap::new();
        per_method.reserve(routes.len().max(1));
        for route in routes {
            let method = normalize_method(&route.method);
            let entry = per_method.entry(method).or_default();
            entry
                .insert(
                    route.path,
                    RouteHandler {
                        handler: Arc::new(route.handler),
                    },
                )
                .map_err(|e| CoreError::InvalidConfig(format!("route conflict: {e}")))?;
        }
        let method_routers = per_method
            .into_iter()
            .map(|(k, v)| (k, Arc::new(v)))
            .collect();
        Ok(Self { method_routers })
    }

    pub fn lookup(&self, method: &str, path: &str) -> Option<LookupResult> {
        let router = self
            .method_routers
            .get(method)
            .or_else(|| self.method_routers.get(&normalize_method(method)))?;
        let found = router.at(path).ok()?;
        let mut params = HashMap::with_capacity(found.params.len());
        for (k, v) in found.params.iter() {
            params.insert(k.to_string(), v.to_string());
        }
        Some(LookupResult {
            handler: found.value.handler.clone(),
            path_params: params,
        })
    }

    pub fn path_exists_for_other_method(&self, method: &str, path: &str) -> bool {
        let normalized = normalize_method(method);
        self.method_routers
            .iter()
            .filter(|(m, _)| m.as_str() != normalized)
            .any(|(_, router)| router.at(path).is_ok())
    }
}

fn normalize_method(method: &str) -> String {
    method.to_ascii_uppercase()
}
