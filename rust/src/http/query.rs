use std::collections::HashMap;

use url::form_urlencoded;

pub fn parse_query(query: Option<&str>) -> HashMap<String, String> {
    let mut out = HashMap::new();
    if let Some(q) = query {
        for (k, v) in form_urlencoded::parse(q.as_bytes()) {
            out.insert(k.into_owned(), v.into_owned());
        }
    }
    out
}
