use std::collections::HashMap;

use bytes::Bytes;

#[derive(Debug, Clone)]
pub struct IncomingRequest {
    pub headers: HashMap<String, String>,
    pub query: HashMap<String, String>,
    pub path_params: HashMap<String, String>,
    pub body: Bytes,
}
