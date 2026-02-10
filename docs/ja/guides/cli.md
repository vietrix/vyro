# CLI User Guide

## Command model

Vyro CLI is split into two surfaces:

1. End-user commands (`vyro ...`) for running and operating applications.
2. Developer scripts (`python -m scripts.dev...`) for internal checks/build/bench.

## End-user commands

- `vyro new` - scaffold a new project.
- `vyro run` - run app in production-style mode.
- `vyro dev` - run app with reload behavior.
- `vyro doctor` - validate environment and readiness hints.
- `vyro openapi` - generate OpenAPI from app routes.
- `vyro compat` - compare API contracts.
- `vyro migrate` - execute migrations.
- `vyro drift` - detect schema drift.
- `vyro k8s` - generate Kubernetes manifests.
- `vyro nogil-tune` - recommend worker tuning.
- `vyro release ...` - release automation commands.

## Developer-only scripts

Use these for project maintenance, not end-user runtime operations:

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## Exit codes

- `0`: success
- `1`: execution/runtime/tooling failure
- `2`: invalid user input/arguments
