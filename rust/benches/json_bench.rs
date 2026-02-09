use criterion::{criterion_group, criterion_main, Criterion};
use serde_json::json;

fn bench_json(c: &mut Criterion) {
    let payload = json!({
        "name": "vyro",
        "ok": true,
        "n": 123,
        "arr": [1, 2, 3, 4]
    });

    c.bench_function("serde_json_to_vec", |b| {
        b.iter(|| {
            let _ = serde_json::to_vec(&payload).unwrap();
        })
    });
}

criterion_group!(benches, bench_json);
criterion_main!(benches);
