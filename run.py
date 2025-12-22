# run.py
import sys
import subprocess


def print_help():
    filename = "run.exe"
    help_text = f"""
사용법: {filename} [옵션]

옵션 목록:
  --setting, -s, setting     설정창(UI) 실행
  --run,     -r, run         ROI 기반 자동 실행
  --dev,     -d, dev         개발 모드로 실행 (로컬호스트 사용)
  --help,    -h, help        도움말 출력

예시:
  {filename} --setting
  {filename} -r
  {filename} -d
  {filename} -h
"""
    print(help_text)


def start():
    
    param_dev = "--dev" if arg in ("--dev", "-d", "dev") else ""
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        # 도움말
        if arg in ("--help", "-h", "help"):
            print_help()
            return

        # 설정창 실행
        if arg in ("--setting", "-s", "setting"):
            subprocess.Popen(["python", "setting.py", param_dev])
            return

        # 자동 작업 실행
        if arg in ("--run", "-r", "run"):
            subprocess.Popen(["python", "main.py", param_dev])
            return

    # 기본 → 자동작업 실행
    subprocess.Popen(["python", "main2.py", param_dev])

if __name__ == "__main__":
    start()
