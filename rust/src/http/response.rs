use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug, Clone)]
pub enum ResponseBody {
    Bytes(Vec<u8>),
    File(PathBuf),
}

#[derive(Debug, Clone)]
pub struct OutgoingResponse {
    pub status: u16,
    pub headers: HashMap<String, String>,
    pub body: ResponseBody,
}

impl Default for OutgoingResponse {
    fn default() -> Self {
        Self {
            status: 200,
            headers: HashMap::new(),
            body: ResponseBody::Bytes(b"".to_vec()),
        }
    }
}
