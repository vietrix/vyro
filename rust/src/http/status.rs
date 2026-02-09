use http::StatusCode;

pub fn not_found_status() -> StatusCode {
    StatusCode::NOT_FOUND
}

pub fn method_not_allowed_status() -> StatusCode {
    StatusCode::METHOD_NOT_ALLOWED
}

pub fn internal_error_status() -> StatusCode {
    StatusCode::INTERNAL_SERVER_ERROR
}
