#[test]
fn response_default_is_200() {
    #[derive(Debug, Clone)]
    struct OutgoingResponse {
        status: u16,
    }

    impl Default for OutgoingResponse {
        fn default() -> Self {
            Self { status: 200 }
        }
    }

    let resp = OutgoingResponse::default();
    assert_eq!(resp.status, 200);
}
