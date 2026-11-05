import tkinter as tk
from tkinter import scrolledtext
from openpyxl import Workbook
import subprocess
import threading
import platform
import time
from datetime import datetime
import ipaddress
import os

class PingTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ping Tester GUI")
        self.root.geometry("720x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f8f8f8")

        self.ip_list = []
        self.running = False
        self.success_count = {}
        self.timeout_count = {}
        self.threads = []
        self.log_records = []  # 로그 누적용
        self.current_hour = datetime.now().strftime("%Y-%m-%d_%H")

        entry_font = ("Arial", 12)
        button_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "relief": "ridge",
            "width": 14,
            "height": 1
        }

        top_frame = tk.Frame(self.root, bg="#f8f8f8")
        top_frame.pack(pady=10, anchor="w", padx=20)

        tk.Label(top_frame, text="IP 주소 입력:", font=entry_font, bg="#f8f8f8").grid(row=0, column=0, padx=(0, 10))
        self.entry = tk.Entry(top_frame, font=entry_font, width=25)
        self.entry.grid(row=0, column=1)

        tk.Button(top_frame, text="Add IP", command=self.add_ip, **button_style).grid(row=0, column=2, padx=10)
        tk.Button(top_frame, text="Save IP List", command=self.save_ip_list_only, **button_style).grid(row=0, column=3)

        list_frame = tk.Frame(self.root, bg="#f8f8f8")
        list_frame.pack(pady=5)

        self.listbox = tk.Listbox(list_frame, font=("Arial", 12), width=70, height=5, borderwidth=2, relief="sunken")
        self.listbox.pack()

        control_frame = tk.Frame(self.root, bg="#f8f8f8")
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Start Ping", command=self.start_ping, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=30)

        self.stop_button = tk.Button(control_frame, text="Stop Ping", command=self.stop_ping, state=tk.DISABLED, **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=30)

        log_frame = tk.Frame(self.root, bg="#f8f8f8")
        log_frame.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=20, width=85, font=("Consolas", 10), borderwidth=2, relief="sunken")
        self.log_area.pack()

        self.log_area.tag_config("success", foreground="green")
        self.log_area.tag_config("timeout", foreground="red")
        self.log_area.tag_config("warning", foreground="orange")
        self.log_area.tag_config("info", foreground="blue")

    def add_ip(self):
        ip = self.entry.get().strip()
        if not ip:
            return
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            self.log_area.insert(tk.END, f"⚠️ [오류] 잘못된 IP 주소입니다: {ip}\n", "warning")
            self.entry.delete(0, tk.END)
            return
        if ip not in self.ip_list:
            self.ip_list.append(ip)
            self.listbox.insert(tk.END, ip)
            self.success_count[ip] = 0
            self.timeout_count[ip] = 0
        self.entry.delete(0, tk.END)

    def save_ip_list_only(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"ip_only_list_{now}.xlsx"
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "IP_List"
            ws.append(["IP Address"])
            for ip in self.ip_list:
                ws.append([ip])
            wb.save(file_path)
            self.log_area.insert(tk.END, f"💾 [IP 목록 저장됨] 파일: {file_path}\n", "info")
        except Exception as e:
            self.log_area.insert(tk.END, f"❌ 저장 실패: {e}\n", "timeout")

    def save_log_to_excel_by_hour(self, force=False):
        now_hour = datetime.now().strftime("%Y-%m-%d_%H")
        if force or now_hour != self.current_hour:
            if self.log_records:
                file_path = f"ping_log_{self.current_hour}.xlsx"
                try:
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Log"
                    ws.append(["Timestamp", "IP Address", "Status", "Message"])
                    for record in self.log_records:
                        ws.append(record)
                    wb.save(file_path)
                    self.log_area.insert(tk.END, f"💾 [로그 저장됨] 파일: {file_path}\n", "info")
                    # # self.log_records.clear()  # 로그를 유지하여 재시작 시에도 누적 저장 가능  # 제거하여 로그를 누적 저장할 수 있도록 함
                except Exception as e:
                    self.log_area.insert(tk.END, f"❌ 로그 저장 실패: {e}\n", "timeout")
            self.current_hour = now_hour

    def ping_loop(self, ip):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        cmd = ['ping', param, '1', ip]
        if platform.system().lower() == 'windows':
            cmd += ['-w', '1000']
        else:
            cmd += ['-W', '1']

        creationflags = subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
        success_keywords = ["Reply from", "응답", "답변", "bytes=", "ttl=", "TTL="]

        while self.running:
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=creationflags
                )
                stdout, _ = process.communicate(timeout=2)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                success_detected = False
                for line in stdout.strip().splitlines():
                    if any(keyword in line for keyword in success_keywords):
                        self.success_count[ip] += 1
                        self.log_area.insert(tk.END, f"✅ [{timestamp}] {line.strip()}\n", "success")
                        self.log_records.append([timestamp, ip, "Success", line.strip()])
                        success_detected = True
                        break

                if not success_detected:
                    self.timeout_count[ip] += 1
                    msg = f"{ip} 요청 시간이 만료되었습니다."
                    self.log_area.insert(tk.END, f"❌ [{timestamp}] {msg}\n", "timeout")
                    self.log_records.append([timestamp, ip, "Timeout", msg])

            except subprocess.TimeoutExpired:
                self.timeout_count[ip] += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = f"{ip} 요청 시간이 만료되었습니다."
                self.log_area.insert(tk.END, f"❌ [{timestamp}] {msg}\n", "timeout")
                self.log_records.append([timestamp, ip, "Timeout", msg])

            self.save_log_to_excel_by_hour()
            self.log_area.see(tk.END)
            time.sleep(1)

    def start_ping(self):
        if not self.ip_list:
            self.log_area.insert(tk.END, "⚠️ IP 리스트가 비어 있습니다.\n", "warning")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"▶️ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping test started...\n", "info")

        # self.threads.clear()  # 중단 후 다시 시작해도 이전 로그 유지
        self.log_records.clear()
        self.current_hour = datetime.now().strftime("%Y-%m-%d_%H")

        for ip in self.ip_list:
            thread = threading.Thread(target=self.ping_loop, args=(ip,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop_ping(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_area.insert(tk.END, f"⏹️ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ping test stopped.\n", "info")

        for thread in self.threads:
            thread.join(timeout=2)

        self.save_log_to_excel_by_hour(force=True)

        for ip in self.ip_list:
            success = self.success_count[ip]
            timeout = self.timeout_count[ip]
            total = success + timeout
            rate = round((success / total) * 100, 1) if total > 0 else 0.0
            summary = f"📊 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {ip} - Success: {success}, Timeout: {timeout}, Rate: {rate}%"
            self.log_area.insert(tk.END, summary + "\n", "info")

        self.log_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PingTesterApp(root)
    root.mainloop()
