import customtkinter as ctk
import tkinter as tk
import json

SETTING_FILE = "setting.json"

def load_settings():
    with open(SETTING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

        
def parse_event_key(event):
    """
    Alt 플래그가 들어가도, 사용자가 실질적으로 Alt/Shift/Ctrl 키를 동시에 '누른' 경우에만 modifier로 기록.
    'w'만 누르면 항상 'w'만 반환.
    """
    # 단독 modifier 키 누르면 무시
    if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
        return None
    if event.keysym == "Escape":
        return "CANCEL"

    mods = []
    # 실제 '눌림'을 직접 감지 (event.state와 상관없이 event.keysym이 'w'면 'w'만 기록)
    # Ctrl+w 등 '동시입력'만 기록: event.state에서 해당 modifier 플래그 + 실제 modifier key가 눌렸을 때만 포함
    if event.state & 0x0004 and event.keysym not in ("Control_L", "Control_R"):
        mods.append("Ctrl")
    if event.state & 0x0001 and event.keysym not in ("Shift_L", "Shift_R"):
        mods.append("Shift")
    # Alt 플래그가 켜져 있어도, 실제로 Alt와 조합입력이 아니면 Alt 제외
    # 보수적으로 Alt 조합 입력은 특별한 경우(Alt+F4 등)에만 허용하는 식도 있음
    if event.state & 0x0008 and event.keysym not in ("Alt_L", "Alt_R"):
        # Alt는 정말 명확하게 Alt 조합일 때만 인식하도록 설정
        mods.append("Alt")
    # 디버그
    print(f"[DEBUG] keysym={event.keysym}, keycode={event.keycode}, char={event.char}, state={event.state}, mods={mods}")
    return "+".join(mods + [event.keysym]) if mods else event.keysym



class SettingEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("setting.json 편집기")
        self.geometry("850x480")
        self.resizable(False, False)
        self.settings = load_settings()
        self.selected_index = None
        self.is_recording_key = False

        # 상단
        topbar = ctk.CTkFrame(self, height=45)
        topbar.pack(fill=tk.X, padx=0, pady=0)
        ctk.CTkLabel(topbar, text="setting.json 편집기", font=("맑은 고딕", 22)).pack(side=tk.LEFT, padx=16)
        ctk.CTkButton(topbar, text="파일에 저장", command=self.save_to_file).pack(side=tk.RIGHT, padx=16, pady=6)

        # 좌우 분할
        content = ctk.CTkFrame(self)
        content.pack(fill=tk.BOTH, expand=True)

        # 왼쪽: 목록
        left = ctk.CTkFrame(content, width=240)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        ctk.CTkLabel(left, text="단축키 목록", font=("맑은 고딕", 15)).pack(anchor="w", padx=5, pady=(0,6))
        self.shortcut_listbox = tk.Listbox(left, width=26, height=23, activestyle='dotbox')
        self.shortcut_listbox.pack(pady=3)
        self.shortcut_listbox.bind('<<ListboxSelect>>', self.on_select)

        btn_frame = ctk.CTkFrame(left)
        btn_frame.pack(pady=6, fill=tk.X)
        ctk.CTkButton(btn_frame, text="+ 추가", command=self.add_shortcut, width=90).pack(side=tk.LEFT, padx=3)
        ctk.CTkButton(btn_frame, text="- 삭제", command=self.delete_shortcut, width=90).pack(side=tk.LEFT, padx=3)

        # 오른쪽: 상세 수정 폼
        right = ctk.CTkFrame(content)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

        # key: Entry(읽기전용) + '키 입력 녹화' 버튼
        ctk.CTkLabel(right, text="키 바인딩 (녹화)", anchor="w", width=90).grid(row=0, column=0, sticky="w", pady=(12,8))
        self.key_var = tk.StringVar()
        self.key_entry = ctk.CTkEntry(right, width=225, textvariable=self.key_var, state="readonly")
        self.key_entry.grid(row=0, column=1, sticky="w", pady=(12,8))
        self.record_btn = ctk.CTkButton(right, text="키 입력 녹화/변경", command=self.start_recording_key, width=140)
        self.record_btn.grid(row=0, column=2, padx=6, sticky="w")

        # action (출력만)
        ctk.CTkLabel(right, text="액션 (읽기전용)", anchor="w", width=90).grid(row=1, column=0, sticky="w", pady=8)
        self.action_entry = ctk.CTkEntry(right, width=300, state="readonly")
        self.action_entry.grid(row=1, column=1, columnspan=2, sticky="w", pady=8)

        # description (출력만)
        ctk.CTkLabel(right, text="설명 (읽기전용)", anchor="w", width=90).grid(row=2, column=0, sticky="w", pady=8)
        self.desc_entry = ctk.CTkEntry(right, width=300, state="readonly")
        self.desc_entry.grid(row=2, column=1, columnspan=2, sticky="w", pady=8)

        # params (출력만, 여러줄)
        ctk.CTkLabel(right, text="params (읽기전용)", anchor="nw", width=90).grid(row=3, column=0, sticky="nw", pady=8)
        self.params_text = tk.Text(right, width=38, height=7, state="disabled", font=("맑은 고딕", 11))
        self.params_text.grid(row=3, column=1, columnspan=2, sticky="w", pady=8)

        # 저장/되돌리기 버튼
        btns = ctk.CTkFrame(right)
        btns.grid(row=4, column=0, columnspan=3, pady=16)
        ctk.CTkButton(btns, text="저장", command=self.save_current, width=120).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(btns, text="되돌리기", command=self.reload_selected, width=120).pack(side=tk.LEFT, padx=6)

        # 하단 도움말
        helpbar = ctk.CTkFrame(self, height=30)
        helpbar.pack(fill=tk.X, side=tk.BOTTOM)
        ctk.CTkLabel(helpbar, text="키 바인딩은 '키 입력 녹화/변경' 버튼으로만 입력합니다. ESC로 취소 가능.",
            font=("맑은 고딕", 12), anchor="w").pack(side=tk.LEFT, padx=10, pady=4)

        self.bind("<Key>", self._on_key_global)  # 앱 전체 키이벤트 처리용

        self.populate_listbox()

    def populate_listbox(self):
        self.shortcut_listbox.delete(0, tk.END)
        for idx, shortcut in enumerate(self.settings["shortcuts"]):
            show = f'{idx+1:02d}. {shortcut["key"]} | {shortcut["action"]}'
            self.shortcut_listbox.insert(tk.END, show)

    def on_select(self, event):
        sel = self.shortcut_listbox.curselection()
        if not sel:
            return
        self.selected_index = sel[0]
        sc = self.settings["shortcuts"][self.selected_index]
        self.key_var.set(sc.get("key", ""))
        # action (read-only)
        self.action_entry.configure(state="normal")
        self.action_entry.delete(0, tk.END)
        self.action_entry.insert(0, sc.get("action", ""))
        self.action_entry.configure(state="readonly")
        # desc (read-only)
        self.desc_entry.configure(state="normal")
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, sc.get("description", ""))
        self.desc_entry.configure(state="readonly")
        # params (read-only)
        self.params_text.configure(state="normal")
        self.params_text.delete(1.0, tk.END)
        params = sc.get("params", {})
        pretty_params = json.dumps(params, ensure_ascii=False, indent=2) if params else ""
        self.params_text.insert(tk.END, pretty_params)
        self.params_text.configure(state="disabled")

    def reload_selected(self):
        self.on_select(None)

    def save_current(self):
        if self.selected_index is None:
            tk.messagebox.showerror("에러", "왼쪽에서 단축키를 먼저 선택하세요.")
            return
        sc = self.settings["shortcuts"][self.selected_index]
        sc["key"] = self.key_var.get()
        self.populate_listbox()

    def save_to_file(self):
        save_settings(self.settings)
        tk.messagebox.showinfo("저장", "setting.json에 저장되었습니다.")

    def add_shortcut(self):
        new_sc = {"key": "", "action": "", "description": "", "params": {}}
        self.settings["shortcuts"].append(new_sc)
        self.populate_listbox()
        self.shortcut_listbox.select_set(tk.END)
        self.on_select(None)

    def delete_shortcut(self):
        sel = self.shortcut_listbox.curselection()
        if not sel:
            tk.messagebox.showerror("에러", "삭제할 단축키를 선택하세요.")
            return
        idx = sel[0]
        del self.settings["shortcuts"][idx]
        self.populate_listbox()
        self.selected_index = None
        self.key_var.set("")
        self.action_entry.configure(state="normal"); self.action_entry.delete(0, tk.END); self.action_entry.configure(state="readonly")
        self.desc_entry.configure(state="normal"); self.desc_entry.delete(0, tk.END); self.desc_entry.configure(state="readonly")
        self.params_text.configure(state="normal"); self.params_text.delete(1.0, tk.END); self.params_text.configure(state="disabled")

    def start_recording_key(self):
        if not self.selected_index is None:
            self.is_recording_key = True
            self.record_btn.configure(text="키 입력 대기중...(ESC:취소)")
            self.key_entry.configure(placeholder_text="키를 눌러주세요")
            self.key_entry.configure(state="normal")
            self.key_entry.delete(0, tk.END)
            self.key_entry.configure(state="readonly")
            self.focus_set()

    def _on_key_global(self, event):
        # 녹화 대기중일 때만 반응
        if not self.is_recording_key:
            return
        keystr = parse_event_key(event)
        if keystr is None:
            return  # 단독 modifier 키는 무시
        if keystr == "CANCEL":
            self.is_recording_key = False
            self.record_btn.configure(text="키 입력 녹화/변경")
            self.reload_selected()
            return
        # 정상 키입력
        self.key_var.set(keystr)
        self.is_recording_key = False
        self.record_btn.configure(text="키 입력 녹화/변경")

if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = SettingEditor()
    app.mainloop()
