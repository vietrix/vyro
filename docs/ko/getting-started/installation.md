# 설치

## 요구 사항

- Python 3.10+
- pip
- Rust toolchain (소스 빌드 시에만 필요)

## PyPI에서 설치

```bash
pip install vyro
```

## 설치 확인

기본 명령(최종 사용자 권장):

```bash
vyro --help
```

대체 방법(`PATH`에 `vyro`가 아직 잡히지 않는 경우):

```bash
python -m vyro --help
```

## 왜 명령이 두 가지인가요?

- `vyro`는 최종 사용자를 위한 공식 CLI 명령입니다.
- `python -m vyro`는 동일한 CLI 모듈을 직접 실행하며, PATH/디버깅 상황에서 유용합니다.

## PATH 문제 해결

`vyro` 명령을 찾을 수 없다면:

1. 설치 후 터미널을 다시 여세요.
2. Python `Scripts` 디렉터리가 PATH에 포함되어 있는지 확인하세요.
3. 임시로 `python -m vyro`를 사용하세요.

## 개발자 환경 설정

```bash
pip install -e .[dev]
pip install -e .[docs]
```
