# Ping 테스터

여러 IP에 1초 간격으로 ping을 보내 응답 여부를 실시간으로 보여주는 Windows 프로그램입니다.
결과는 시간대별 엑셀 파일로 저장되고, 중지하면 IP별 성공률을 요약해 줍니다.

## 실행

Python 3과 openpyxl이 필요합니다.

```
pip install -r requirements.txt
python ping_tester.py
```

로그 파일은 프로그램을 실행한 폴더에 저장됩니다.

## 실행 파일 만들기

```
pip install pyinstaller openpyxl
pyinstaller ping_tester.spec
```

결과물은 `dist` 폴더에 생깁니다.

## 사용한 구성요소

- [openpyxl](https://openpyxl.readthedocs.io/) (MIT 라이선스): 엑셀 파일 저장
- Python 표준 라이브러리, Tkinter

## 라이선스

[MIT](LICENSE) © 최승훈
