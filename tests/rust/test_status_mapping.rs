#[test]
fn status_code_constants_are_correct() {
    assert_eq!(http::StatusCode::NOT_FOUND.as_u16(), 404);
    assert_eq!(http::StatusCode::METHOD_NOT_ALLOWED.as_u16(), 405);
}
