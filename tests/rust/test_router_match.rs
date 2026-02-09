#[test]
fn matchit_params_and_wildcard_work() {
    let mut router = matchit::Router::new();
    router.insert("/users/{id}", "users").unwrap();
    router.insert("/static/{*wildcard}", "static").unwrap();

    let user = router.at("/users/42").unwrap();
    assert_eq!(user.value, &"users");
    assert_eq!(user.params.get("id"), Some("42"));

    let file = router.at("/static/js/app.js").unwrap();
    assert_eq!(file.value, &"static");
    assert_eq!(file.params.get("wildcard"), Some("js/app.js"));
}
