# 설치

## 요구 사항

- 파이썬 3.10+
-핍
- Rust 툴체인(소스 빌드에만 필요)

## PyPI에서 설치

```bash
pip install vyro
```

## 설치 확인

기본(최종 사용자에게 권장):

```bash
vyro --help
```

대체(쉘 PATH가 아직 `vyro`를 노출하지 않는 경우):

```bash
python -m vyro --help
```

## 왜 명령이 두 개인가요?

- `vyro`는 공식 최종 사용자 CLI 명령입니다.
- `python -m vyro`는 동일한 CLI 모듈을 직접 실행하며 PATH/디버그 시나리오에 유용합니다.

## PATH 문제 해결

`vyro`를 찾을 수 없는 경우:

1. 설치 후 터미널을 다시 엽니다.
2. Python 스크립트 디렉터리가 PATH에 있는지 확인하세요.
3. 임시로 `python -m vyro`를 사용하세요.

## 개발자 설정

```bash
pip install -e .[dev]
pip install -e .[docs]
```
