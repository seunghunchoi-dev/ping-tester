# Ping 테스터

여러 IP에 1초 간격으로 ping을 보내 응답 여부를 실시간으로 보여주는 Windows 프로그램입니다.
결과는 시간대별 엑셀 파일로 저장되고, 중지하면 IP별 성공률을 요약해 줍니다.

## 내려받기

Python을 설치하지 않아도 바로 쓸 수 있습니다. [Releases](https://github.com/seunghunchoi-dev/ping-tester/releases/latest)에서 zip 파일을 받아 압축을 풀고 `ping_tester.exe`를 실행하세요.

'Windows의 PC 보호' 창이 뜨면 **[추가 정보] → [실행]** 을 누르세요. 코드 서명이 없는 개인 배포 프로그램이라 나타나는 안내입니다.

## 소스에서 실행

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

실행 파일에 포함된 구성요소의 고지는 [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt)에 있습니다.

## 라이선스

[MIT](LICENSE) © 최승훈
