use criterion::{criterion_group, criterion_main, Criterion};
use matchit::Router;

fn bench_routing(c: &mut Criterion) {
    let mut router = Router::new();
    router.insert("/users/{id}", 1usize).unwrap();
    router.insert("/static/{*rest}", 2usize).unwrap();

    c.bench_function("matchit_lookup_users", |b| {
        b.iter(|| {
            let _ = router.at("/users/123").unwrap();
        })
    });
}

criterion_group!(benches, bench_routing);
criterion_main!(benches);
