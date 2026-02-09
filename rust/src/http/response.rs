use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct OutgoingResponse {
    pub status: u16,
    pub headers: HashMap<String, String>,
    pub body: Vec<u8>,
}

impl Default for OutgoingResponse {
    fn default() -> Self {
        Self {
            status: 200,
            headers: HashMap::new(),
            body: b"".to_vec(),
        }
    }
}
