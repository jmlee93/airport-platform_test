# Excel 재무 모델 리포트 도구 (예시)

이 저장소는 "엑셀 재무 모델 자동 해석/리포트 생성" 아이디어를 구현하기 위한 최소 예시 구조를 포함합니다. 
현재 버전은 엑셀 파일의 시트와 수식을 요약해 JSON으로 출력하는 간단한 스크립트만을 제공합니다.

## 구성 요소

- `src/excel_reporter/cli.py` – 명령행 인터페이스와 기본 분석 로직. 
- `src/excel_reporter/__main__.py` – `python -m excel_reporter`로 실행할 수 있도록 진입점을 제공합니다.
- `requirements.txt` – 필요한 파이썬 패키지 목록 (현재는 `openpyxl`).

## 설치 및 실행 방법

1. 파이썬 3.10 이상이 설치되어 있다고 가정합니다.
2. 가상환경을 만든 뒤 의존성을 설치합니다.

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows에서는 `.venv\\Scripts\\activate`
   pip install -r requirements.txt
   ```

3. 분석할 엑셀 파일을 준비하고 다음 명령으로 실행합니다.

   ```bash
   python -m excel_reporter path/to/workbook.xlsx --output summary.json
   ```

   `--output` 옵션을 생략하면 표준 출력으로 JSON을 확인할 수 있습니다.

## 다음 단계 아이디어

- 수식 의존성 그래프 작성 및 시각화
- 민감도(시나리오) 분석 엔진 구현
- Markdown/PDF/PowerPoint 등으로 리포트 자동 생성
- Streamlit/FastAPI 등으로 웹 대시보드 구축

이 예시를 기반으로 점진적으로 기능을 확장해 나갈 수 있습니다.
