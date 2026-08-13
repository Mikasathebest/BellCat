#!/usr/bin/env python3
"""BellCat cross-platform desktop app for Windows and Linux."""

import json
import math
import os
import platform
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

APP_NAME = "BellCat"
VERSION = "2.0.0"
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home() / ".config")) / "BellCat"
CONFIG_FILE = CONFIG_DIR / "settings.json"

LANGUAGES = {
    "中文": {"timer": "番茄钟", "reminders": "提醒", "start": "开始", "pause": "暂停", "reset": "重置", "new": "新建", "settings": "设置", "work": "工作", "rest": "休息", "other": "其他", "task": "任务", "minutes": "分钟", "save": "保存", "cancel": "取消", "title": "名称", "date": "日期 YYYY-MM-DD", "clock": "时间 HH:MM", "advance": "提前分钟", "alarm": "闹钟", "notification": "通知", "no_reminders": "还没有提醒", "theme": "主题", "light": "浅色", "dark": "深色", "language": "语言", "add_stage": "添加阶段", "completed": "已完成 {n} 轮", "hint": "点击色段或拖动圆点", "due": "提醒时间到：{title}"},
    "English": {"timer": "Timer", "reminders": "Reminders", "start": "Start", "pause": "Pause", "reset": "Reset", "new": "New", "settings": "Settings", "work": "Work", "rest": "Break", "other": "Other", "task": "Task", "minutes": "minutes", "save": "Save", "cancel": "Cancel", "title": "Name", "date": "Date YYYY-MM-DD", "clock": "Time HH:MM", "advance": "Minutes early", "alarm": "Alarm", "notification": "Notification", "no_reminders": "No reminders yet", "theme": "Theme", "light": "Light", "dark": "Dark", "language": "Language", "add_stage": "Add stage", "completed": "{n} round(s) completed", "hint": "Click a segment or drag the dot", "due": "Reminder: {title}"},
    "日本語": {"timer": "タイマー", "reminders": "リマインダー", "start": "開始", "pause": "一時停止", "reset": "リセット", "new": "新規", "settings": "設定", "work": "作業", "rest": "休憩", "other": "その他", "task": "タスク", "minutes": "分", "save": "保存", "cancel": "キャンセル", "title": "名前", "date": "日付 YYYY-MM-DD", "clock": "時刻 HH:MM", "advance": "何分前", "alarm": "アラーム", "notification": "通知", "no_reminders": "リマインダーはありません", "theme": "テーマ", "light": "ライト", "dark": "ダーク", "language": "言語", "add_stage": "ステージを追加", "completed": "{n}セット完了", "hint": "セグメントをクリック、または点をドラッグ", "due": "リマインダー：{title}"},
    "Español": {"timer": "Temporizador", "reminders": "Recordatorios", "start": "Iniciar", "pause": "Pausar", "reset": "Reiniciar", "new": "Nuevo", "settings": "Ajustes", "work": "Trabajo", "rest": "Descanso", "other": "Otro", "task": "Tarea", "minutes": "minutos", "save": "Guardar", "cancel": "Cancelar", "title": "Nombre", "date": "Fecha YYYY-MM-DD", "clock": "Hora HH:MM", "advance": "Minutos antes", "alarm": "Alarma", "notification": "Notificación", "no_reminders": "No hay recordatorios", "theme": "Tema", "light": "Claro", "dark": "Oscuro", "language": "Idioma", "add_stage": "Añadir etapa", "completed": "{n} ronda(s) completada(s)", "hint": "Haz clic o arrastra el punto", "due": "Recordatorio: {title}"},
    "Français": {"timer": "Minuteur", "reminders": "Rappels", "start": "Démarrer", "pause": "Pause", "reset": "Réinitialiser", "new": "Nouveau", "settings": "Réglages", "work": "Travail", "rest": "Pause", "other": "Autre", "task": "Tâche", "minutes": "minutes", "save": "Enregistrer", "cancel": "Annuler", "title": "Nom", "date": "Date AAAA-MM-JJ", "clock": "Heure HH:MM", "advance": "Minutes avant", "alarm": "Alarme", "notification": "Notification", "no_reminders": "Aucun rappel", "theme": "Thème", "light": "Clair", "dark": "Sombre", "language": "Langue", "add_stage": "Ajouter une étape", "completed": "{n} cycle(s) terminé(s)", "hint": "Cliquez ou faites glisser le point", "due": "Rappel : {title}"},
    "العربية": {"timer": "المؤقت", "reminders": "التذكيرات", "start": "ابدأ", "pause": "إيقاف", "reset": "إعادة", "new": "جديد", "settings": "الإعدادات", "work": "عمل", "rest": "استراحة", "other": "أخرى", "task": "مهمة", "minutes": "دقائق", "save": "حفظ", "cancel": "إلغاء", "title": "الاسم", "date": "التاريخ YYYY-MM-DD", "clock": "الوقت HH:MM", "advance": "دقائق قبل", "alarm": "منبّه", "notification": "إشعار", "no_reminders": "لا توجد تذكيرات", "theme": "السمة", "light": "فاتح", "dark": "داكن", "language": "اللغة", "add_stage": "إضافة مرحلة", "completed": "اكتملت {n} جولة", "hint": "انقر أو اسحب النقطة", "due": "تذكير: {title}"},
    "한국어": {"timer": "타이머", "reminders": "알림", "start": "시작", "pause": "일시 정지", "reset": "초기화", "new": "새로 만들기", "settings": "설정", "work": "작업", "rest": "휴식", "other": "기타", "task": "작업", "minutes": "분", "save": "저장", "cancel": "취소", "title": "이름", "date": "날짜 YYYY-MM-DD", "clock": "시간 HH:MM", "advance": "미리 알림(분)", "alarm": "알람", "notification": "알림", "no_reminders": "알림이 없습니다", "theme": "테마", "light": "라이트", "dark": "다크", "language": "언어", "add_stage": "단계 추가", "completed": "{n}회 완료", "hint": "단계를 클릭하거나 점을 드래그", "due": "알림: {title}"},
}

QUOTES = [
    ("Our doubts are traitors, and make us lose the good we oft might win.", "Shakespeare"),
    ("Never give in—never, never, never, never.", "Winston Churchill"),
    ("When you have eliminated the impossible, whatever remains must be the truth.", "Sherlock Holmes"),
    ("All for one, one for all.", "The Three Musketeers"),
    ("Wait and hope.", "The Count of Monte Cristo"),
]

DEFAULT = {
    "language": "中文", "theme": "light", "completed": 0,
    "tasks": [{"name": "Focus", "stages": [
        {"name": "Work", "minutes": 25, "color": "#F3A83B"},
        {"name": "Break", "minutes": 5, "color": "#58BFA8"}]}],
    "selected_task": 0, "reminders": []
}


def load_config():
    try:
        return {**DEFAULT, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    except Exception:
        return json.loads(json.dumps(DEFAULT))


def save_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class BellCat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = load_config()
        self.lang = LANGUAGES.get(self.data["language"], LANGUAGES["English"])
        self.title(f"BellCat {VERSION}")
        self.geometry("780x720")
        self.minsize(650, 600)
        self.running = False
        self.stage_index = 0
        self.seconds_left = self.stage["minutes"] * 60
        self.last_tick = time.monotonic()
        self.configure_ui()
        self.after(250, self.tick)
        self.after(1000, self.check_reminders)

    @property
    def task(self): return self.data["tasks"][self.data["selected_task"]]
    @property
    def stage(self): return self.task["stages"][self.stage_index]

    def configure_ui(self):
        for child in self.winfo_children(): child.destroy()
        dark = self.data["theme"] == "dark"
        self.bg = "#211B18" if dark else "#FFF9F0"
        self.fg = "#F7EBDD" if dark else "#3D2A20"
        self.card = "#332923" if dark else "#FFFFFF"
        self.configure(bg=self.bg)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.fg)
        style.configure("TButton", padding=8)

        top = ttk.Frame(self); top.pack(fill="x", padx=22, pady=18)
        ttk.Button(top, text="＋", width=3, command=self.new_menu).pack(side="left")
        quote, author = QUOTES[int(time.time()) % len(QUOTES)]
        ttk.Label(top, text=f'“{quote}”\n— {author}', font=("TkDefaultFont", 10)).pack(side="left", padx=14)
        ttk.Label(top, text="BellCat", font=("TkDefaultFont", 20, "bold"), foreground="#E58632").pack(side="right")
        ttk.Button(top, text="⚙", width=3, command=self.settings_dialog).pack(side="right", padx=8)

        nav = ttk.Frame(self); nav.pack(pady=4)
        ttk.Button(nav, text=self.lang["timer"], command=self.show_timer).pack(side="left", padx=4)
        ttk.Button(nav, text=self.lang["reminders"], command=self.show_reminders).pack(side="left", padx=4)
        self.content = ttk.Frame(self); self.content.pack(fill="both", expand=True, padx=22, pady=12)
        self.show_timer()

    def clear_content(self):
        for child in self.content.winfo_children(): child.destroy()

    def show_timer(self):
        self.clear_content()
        names = [task["name"] for task in self.data["tasks"]]
        self.task_var = tk.StringVar(value=self.task["name"])
        picker = ttk.Combobox(self.content, textvariable=self.task_var, values=names, state="readonly", width=28)
        picker.pack(pady=4); picker.bind("<<ComboboxSelected>>", self.select_task)
        self.canvas = tk.Canvas(self.content, width=410, height=410, bg=self.bg, highlightthickness=0)
        self.canvas.pack(pady=6)
        self.canvas.bind("<Button-1>", self.seek_ring); self.canvas.bind("<B1-Motion>", self.seek_ring)
        controls = ttk.Frame(self.content); controls.pack(pady=8)
        ttk.Button(controls, text=self.lang["reset"], command=self.reset).pack(side="left", padx=6)
        self.start_button = ttk.Button(controls, text=self.lang["pause"] if self.running else self.lang["start"], command=self.toggle)
        self.start_button.pack(side="left", padx=6)
        self.completed_label = ttk.Label(self.content, text=self.lang["completed"].format(n=self.data["completed"]))
        self.completed_label.pack(pady=6)
        self.draw_ring()

    def draw_ring(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        x0, y0, x1, y1 = 38, 38, 372, 372
        total = sum(s["minutes"] for s in self.task["stages"])
        angle = 90
        elapsed_before = 0
        for i, stage in enumerate(self.task["stages"]):
            extent = -360 * stage["minutes"] / total
            self.canvas.create_arc(x0, y0, x1, y1, start=angle, extent=extent, style="arc",
                                   width=29 if i == self.stage_index else 22, outline=stage["color"])
            angle += extent
            if i < self.stage_index: elapsed_before += stage["minutes"] * 60
        elapsed = elapsed_before + self.stage["minutes"] * 60 - self.seconds_left
        fraction = elapsed / max(1, total * 60)
        theta = fraction * 2 * math.pi - math.pi / 2
        px, py = 205 + 167 * math.cos(theta), 205 + 167 * math.sin(theta)
        self.canvas.create_oval(px-10, py-10, px+10, py+10, fill="white", outline=self.stage["color"], width=4)
        self.canvas.create_text(205, 170, text=self.stage["name"], fill=self.stage["color"], font=("TkDefaultFont", 15, "bold"))
        self.canvas.create_text(205, 215, text=f"{self.seconds_left//60:02d}:{self.seconds_left%60:02d}", fill=self.fg, font=("TkDefaultFont", 42, "bold"))
        self.canvas.create_text(205, 260, text=self.lang["hint"], fill="#888888", font=("TkDefaultFont", 10))

    def seek_ring(self, event):
        dx, dy = event.x - 205, event.y - 205
        fraction = ((math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
        target = fraction * sum(s["minutes"] for s in self.task["stages"]) * 60
        cursor = 0
        for i, stage in enumerate(self.task["stages"]):
            duration = stage["minutes"] * 60
            if target < cursor + duration:
                self.stage_index = i; self.seconds_left = max(1, int(duration - (target - cursor))); break
            cursor += duration
        self.draw_ring()

    def select_task(self, _event=None):
        self.data["selected_task"] = [t["name"] for t in self.data["tasks"]].index(self.task_var.get())
        save_config(self.data); self.reset(); self.show_timer()

    def toggle(self):
        self.running = not self.running; self.last_tick = time.monotonic()
        self.start_button.configure(text=self.lang["pause"] if self.running else self.lang["start"])

    def reset(self):
        self.running = False; self.stage_index = 0; self.seconds_left = self.stage["minutes"] * 60; self.draw_ring()

    def tick(self):
        if self.running and time.monotonic() - self.last_tick >= 1:
            ticks = int(time.monotonic() - self.last_tick); self.last_tick += ticks
            self.seconds_left -= ticks
            if self.seconds_left <= 0:
                self.bell(); self.stage_index = (self.stage_index + 1) % len(self.task["stages"])
                if self.stage_index == 0: self.data["completed"] += 1; save_config(self.data)
                self.seconds_left = self.stage["minutes"] * 60
            self.draw_ring()
        self.after(200, self.tick)

    def new_menu(self):
        popup = tk.Menu(self, tearoff=False)
        popup.add_command(label=self.lang["task"], command=self.new_task)
        popup.add_command(label=self.lang["reminders"], command=self.new_reminder)
        popup.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def new_task(self):
        name = simpledialog.askstring(self.lang["task"], self.lang["title"], parent=self)
        if not name: return
        stages = []
        colors = ["#F3A83B", "#58BFA8", "#ED6A5A", "#7A8EDB", "#B67AD9"]
        while True:
            stage_name = simpledialog.askstring(self.lang["add_stage"], self.lang["title"], parent=self)
            if not stage_name: break
            minutes = simpledialog.askinteger(self.lang["minutes"], self.lang["minutes"], minvalue=1, maxvalue=240, parent=self)
            if minutes: stages.append({"name": stage_name, "minutes": minutes, "color": colors[len(stages) % len(colors)]})
            if not messagebox.askyesno(self.lang["add_stage"], self.lang["add_stage"], parent=self): break
        if stages:
            self.data["tasks"].append({"name": name, "stages": stages}); self.data["selected_task"] = len(self.data["tasks"]) - 1
            save_config(self.data); self.reset(); self.show_timer()

    def show_reminders(self):
        self.clear_content()
        ttk.Button(self.content, text=f"＋ {self.lang['new']}", command=self.new_reminder).pack(anchor="ne", pady=6)
        if not self.data["reminders"]: ttk.Label(self.content, text=self.lang["no_reminders"], font=("TkDefaultFont", 16)).pack(expand=True); return
        for reminder in sorted(self.data["reminders"], key=lambda r: r["fire"]):
            frame = ttk.Frame(self.content); frame.pack(fill="x", pady=7)
            ttk.Label(frame, text="⏰" if reminder["style"] == "alarm" else "🔔", font=("TkDefaultFont", 18)).pack(side="left")
            ttk.Label(frame, text=f"{reminder['title']}\n{reminder['event'].replace('T', ' ')}", font=("TkDefaultFont", 12)).pack(side="left", padx=10)
            ttk.Button(frame, text="×", command=lambda r=reminder: self.delete_reminder(r)).pack(side="right")

    def new_reminder(self):
        title = simpledialog.askstring(self.lang["reminders"], self.lang["title"], parent=self)
        if not title: return
        date = simpledialog.askstring(self.lang["reminders"], self.lang["date"], initialvalue=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"), parent=self)
        clock = simpledialog.askstring(self.lang["reminders"], self.lang["clock"], initialvalue="09:00", parent=self)
        advance = simpledialog.askinteger(self.lang["reminders"], self.lang["advance"], initialvalue=0, minvalue=0, parent=self)
        try: event = datetime.strptime(f"{date} {clock}", "%Y-%m-%d %H:%M")
        except Exception: messagebox.showerror(APP_NAME, "Invalid date/time", parent=self); return
        alarm = messagebox.askyesno(self.lang["alarm"], self.lang["alarm"], parent=self)
        fire = event - timedelta(minutes=advance or 0)
        self.data["reminders"].append({"title": title, "event": event.isoformat(timespec="minutes"), "fire": fire.isoformat(timespec="seconds"), "style": "alarm" if alarm else "notification", "fired": False})
        save_config(self.data); self.show_reminders()

    def delete_reminder(self, reminder):
        self.data["reminders"].remove(reminder); save_config(self.data); self.show_reminders()

    def check_reminders(self):
        now = datetime.now()
        for reminder in self.data["reminders"]:
            if not reminder.get("fired") and datetime.fromisoformat(reminder["fire"]) <= now:
                reminder["fired"] = True; save_config(self.data); self.notify(reminder)
        self.after(1000, self.check_reminders)

    def notify(self, reminder):
        title = self.lang["due"].format(title=reminder["title"])
        self.bell()
        if platform.system() == "Windows":
            try:
                import winsound; winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception: pass
        elif platform.system() == "Linux":
            try: subprocess.Popen(["notify-send", "BellCat", title])
            except Exception: pass
        self.after(10, lambda: messagebox.showinfo("BellCat", title, parent=self))

    def settings_dialog(self):
        win = tk.Toplevel(self); win.title(self.lang["settings"]); win.geometry("360x240"); win.transient(self); win.grab_set()
        ttk.Label(win, text=self.lang["language"]).pack(pady=(20,4))
        language = ttk.Combobox(win, values=list(LANGUAGES), state="readonly"); language.set(self.data["language"]); language.pack()
        ttk.Label(win, text=self.lang["theme"]).pack(pady=(18,4))
        theme = ttk.Combobox(win, values=["light", "dark"], state="readonly"); theme.set(self.data["theme"]); theme.pack()
        def apply():
            self.data["language"] = language.get(); self.data["theme"] = theme.get(); save_config(self.data)
            self.lang = LANGUAGES[self.data["language"]]; win.destroy(); self.configure_ui()
        ttk.Button(win, text=self.lang["save"], command=apply).pack(pady=25)


if __name__ == "__main__":
    BellCat().mainloop()
