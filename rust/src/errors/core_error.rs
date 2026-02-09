use std::error::Error as StdError;
use std::fmt::{Display, Formatter};

#[derive(Debug)]
pub enum CoreError {
    Io(std::io::Error),
    Hyper(hyper::Error),
    Py(pyo3::PyErr),
    InvalidConfig(String),
    ResponseBuild(String),
}

impl Display for CoreError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Io(e) => write!(f, "io error: {e}"),
            Self::Hyper(e) => write!(f, "hyper error: {e}"),
            Self::Py(e) => write!(f, "python error: {e}"),
            Self::InvalidConfig(msg) => write!(f, "invalid config: {msg}"),
            Self::ResponseBuild(msg) => write!(f, "response build error: {msg}"),
        }
    }
}

impl StdError for CoreError {}

impl From<std::io::Error> for CoreError {
    fn from(value: std::io::Error) -> Self {
        Self::Io(value)
    }
}

impl From<hyper::Error> for CoreError {
    fn from(value: hyper::Error) -> Self {
        Self::Hyper(value)
    }
}

impl From<pyo3::PyErr> for CoreError {
    fn from(value: pyo3::PyErr) -> Self {
        Self::Py(value)
    }
}
