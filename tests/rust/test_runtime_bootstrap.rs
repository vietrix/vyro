#[test]
fn runtime_builder_smoke() {
    let rt = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build();
    assert!(rt.is_ok());
}
