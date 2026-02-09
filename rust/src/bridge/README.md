# bridge

## Purpose
Bridge between Python objects and Rust execution model.

## Owns
- Python entrypoint exposed by PyO3.
- Route table parsing from Python.
- Context and response mapping.
- Async callback execution.

## Entry Points
- `py_entry::start_server`

## Not Here
- Socket accept loop and routing data structures.
