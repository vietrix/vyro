# 문제 해결

## `Invalid --app format`

`<module>:<attribute>`(예: `examples.hello_world:app`)를 사용합니다.

## 경로 서명 오류

핸들러가 `async def`이고 첫 번째 인수가 `ctx`인지 확인하세요.

## 네이티브 빌드 문제

Rust 툴체인을 설치하고 `maturin build --release`로 다시 빌드하세요.

## 문서 빌드 오류

`mkdocs build --strict`를 실행하고 끊어진 링크나 누락된 페이지를 수정하세요.