use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;

use bytes::Bytes;
use http::header::{HeaderValue, CONTENT_TYPE};
use http::{Request, Response, StatusCode};
use http_body_util::{BodyExt, Full};
use hyper::body::Incoming;
use hyper::service::service_fn;
use hyper_util::rt::{TokioExecutor, TokioIo};
use hyper_util::server::conn::auto::Builder;
use tokio::net::TcpListener;

use crate::bridge::callback::call_python_handler;
use crate::errors::core_error::CoreError;
use crate::http::headers::{header_name, header_value};
use crate::http::query::parse_query;
use crate::http::request::IncomingRequest;
use crate::http::response::OutgoingResponse;
use crate::http::status::{internal_error_status, method_not_allowed_status, not_found_status};
use crate::routing::method_table::RouteRegistry;
use crate::serialization::content_type::TEXT_PLAIN_UTF8;

type Body = Full<Bytes>;

pub async fn serve(host: String, port: u16, registry: RouteRegistry) -> Result<(), CoreError> {
    let addr: SocketAddr = format!("{host}:{port}")
        .parse()
        .map_err(|e| CoreError::InvalidConfig(format!("invalid host/port: {e}")))?;

    let listener = TcpListener::bind(addr).await?;
    let state = Arc::new(registry);

    loop {
        let (stream, _) = listener.accept().await?;
        let io = TokioIo::new(stream);
        let state = state.clone();
        tokio::spawn(async move {
            let service = service_fn(move |req| handle_request(req, state.clone()));
            let builder = Builder::new(TokioExecutor::new());
            if let Err(err) = builder.serve_connection_with_upgrades(io, service).await {
                eprintln!("connection error: {err}");
            }
        });
    }
}

async fn handle_request(
    req: Request<Incoming>,
    registry: Arc<RouteRegistry>,
) -> Result<Response<Body>, hyper::Error> {
    match process_request(req, registry).await {
        Ok(resp) => Ok(resp),
        Err(err) => Ok(internal_error_response(err)),
    }
}

async fn process_request(
    req: Request<Incoming>,
    registry: Arc<RouteRegistry>,
) -> Result<Response<Body>, CoreError> {
    let method = req.method().as_str().to_string();
    let path = req.uri().path().to_string();

    let lookup = if let Some(found) = registry.lookup(&method, &path) {
        found
    } else if registry.path_exists_for_other_method(&method, &path) {
        return Ok(simple_response(
            method_not_allowed_status(),
            b"Method Not Allowed".to_vec(),
            TEXT_PLAIN_UTF8,
        ));
    } else {
        return Ok(simple_response(
            not_found_status(),
            b"Not Found".to_vec(),
            TEXT_PLAIN_UTF8,
        ));
    };

    let (parts, body) = req.into_parts();
    let body_bytes = body
        .collect()
        .await
        .map_err(CoreError::from)?
        .to_bytes()
        .to_vec();
    let headers = parts
        .headers
        .iter()
        .map(|(k, v)| {
            (
                k.as_str().to_string(),
                v.to_str().unwrap_or_default().to_string(),
            )
        })
        .collect::<HashMap<_, _>>();
    let query = parse_query(parts.uri.query());

    let request = IncomingRequest {
        headers,
        query,
        path_params: lookup.path_params,
        body: body_bytes,
    };

    let response = call_python_handler(lookup.handler, request).await?;
    to_hyper_response(response)
}

fn to_hyper_response(out: OutgoingResponse) -> Result<Response<Body>, CoreError> {
    let status = StatusCode::from_u16(out.status)
        .map_err(|e| CoreError::ResponseBuild(format!("invalid status code: {e}")))?;
    let mut builder = Response::builder().status(status);
    for (k, v) in out.headers {
        builder = builder.header(header_name(&k)?, header_value(&v)?);
    }
    builder
        .body(Full::new(Bytes::from(out.body)))
        .map_err(|e| CoreError::ResponseBuild(format!("failed to build response: {e}")))
}

fn simple_response(status: StatusCode, body: Vec<u8>, content_type: &str) -> Response<Body> {
    let mut resp = Response::new(Full::new(Bytes::from(body)));
    *resp.status_mut() = status;
    resp.headers_mut().insert(
        CONTENT_TYPE,
        HeaderValue::from_str(content_type).unwrap_or(HeaderValue::from_static("text/plain")),
    );
    resp
}

fn internal_error_response(err: CoreError) -> Response<Body> {
    eprintln!("internal error: {err}");
    simple_response(
        internal_error_status(),
        b"Internal Server Error".to_vec(),
        TEXT_PLAIN_UTF8,
    )
}
