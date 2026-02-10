use std::collections::HashMap;

use bytes::Bytes;

use vyro_native::http::request::IncomingRequest;

#[test]
fn incoming_request_body_uses_ref_counted_bytes() {
    let shared = Bytes::from_static(b"payload");
    let request = IncomingRequest {
        headers: HashMap::new(),
        query: HashMap::new(),
        path_params: HashMap::new(),
        body: shared.clone(),
    };

    assert_eq!(request.body, shared);
    assert_eq!(request.body.as_ptr(), shared.as_ptr());
}
