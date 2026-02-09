#![allow(dead_code)]

#[derive(Default)]
pub struct MiddlewareChain;

impl MiddlewareChain {
    pub fn new() -> Self {
        Self
    }
}
