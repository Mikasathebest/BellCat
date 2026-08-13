#!/usr/bin/env python3
"""BellCat cross-platform desktop app for Windows and Linux."""

import json
import math
import os
import platform
import random
import struct
import subprocess
import threading
import time
import tkinter as tk
import wave
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

import pygame

APP_NAME = "BellCat"
VERSION = "2.2.0"
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
    {"en": "Our doubts are traitors, and make us lose the good we oft might win.", "中文": "我们的疑虑是叛徒，常使我们失去本可赢得的美好。", "日本語": "疑いは裏切り者。手にできたはずの幸運を失わせる。", "Español": "Nuestras dudas son traidoras y nos hacen perder el bien que podríamos ganar.", "Français": "Nos doutes sont des traîtres et nous font perdre le bien que nous pourrions gagner.", "العربية": "شكوكنا خائنة، فهي تجعلنا نفقد الخير الذي كان بوسعنا أن نناله.", "한국어": "의심은 배신자라서, 얻을 수 있었던 좋은 것을 잃게 한다.", "source": "Shakespeare · Measure for Measure"},
    {"en": "Never give in—never, never, never, never.", "中文": "永不屈服——永远、永远、永远、永远不要。", "日本語": "決して屈するな。決して、決して、決して、決して。", "Español": "Nunca cedas; nunca, nunca, nunca, nunca.", "Français": "Ne cédez jamais — jamais, jamais, jamais, jamais.", "العربية": "لا تستسلم أبداً—أبداً، أبداً، أبداً، أبداً.", "한국어": "절대 굴복하지 마라. 절대, 절대, 절대, 절대로.", "source": "Winston Churchill"},
    {"en": "When you have eliminated the impossible, whatever remains must be the truth.", "中文": "排除一切不可能之后，剩下的无论多么不可思议，都必是真相。", "日本語": "不可能なものを除けば、残ったものが真実である。", "Español": "Cuando has eliminado lo imposible, lo que queda debe ser la verdad.", "Français": "Lorsque vous avez éliminé l’impossible, ce qui reste doit être la vérité.", "العربية": "حين تستبعد المستحيل، فلا بد أن يكون ما تبقّى هو الحقيقة.", "한국어": "불가능한 것을 제거하고 나면, 남은 것이 진실이다.", "source": "Sherlock Holmes · The Sign of Four"},
    {"en": "All for one, one for all.", "中文": "人人为我，我为人人。", "日本語": "一人は皆のために、皆は一人のために。", "Español": "Todos para uno y uno para todos.", "Français": "Tous pour un, un pour tous.", "العربية": "الكل للواحد، والواحد للكل.", "한국어": "모두는 하나를 위해, 하나는 모두를 위해.", "source": "The Three Musketeers"},
    {"en": "Wait and hope.", "中文": "等待，并心怀希望。", "日本語": "待て、しかして希望せよ。", "Español": "Esperar y confiar.", "Français": "Attendre et espérer.", "العربية": "انتظر وكن على أمل.", "한국어": "기다려라, 그리고 희망을 가져라.", "source": "The Count of Monte Cristo"},
]

DEFAULT = {
    "language": "中文", "theme": "light", "completed": 0,
    "tasks": [{"name": "Focus", "stages": [
        {"name": "Work", "minutes": 25, "color": "#4B4D51"},
        {"name": "Break", "minutes": 5, "color": "#A7A9AD"}]}],
    "selected_task": 0, "reminders": [], "ambience": "ocean"
}

PRESET_TASKS = [
    {"name": "专注工作", "stages": [{"name": "Work", "minutes": 30, "color": "#4B4D51"}, {"name": "Break", "minutes": 3, "color": "#A7A9AD"}]},
    {"name": "番茄时钟", "stages": [{"name": "Work", "minutes": 25, "color": "#4B4D51"}, {"name": "Break", "minutes": 5, "color": "#A7A9AD"}]},
    {"name": "课程学习", "stages": [{"name": "Study", "minutes": 40, "color": "#4B4D51"}, {"name": "Break", "minutes": 10, "color": "#A7A9AD"}]},
]

AMBIENCE_NAMES = {"ocean": "Ocean Waves", "wind": "Wind", "rain": "Rain", "rainforest": "Rainforest Birds", "custom": "My Music"}


def load_config():
    try:
        data = {**DEFAULT, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    except Exception:
        data = json.loads(json.dumps(DEFAULT))
    names = {task["name"] for task in data["tasks"]}
    data["tasks"].extend(json.loads(json.dumps(task)) for task in PRESET_TASKS if task["name"] not in names)
    return data


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
        self.ambience_playing = False
        self.custom_music = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.audio_ready = True
        except Exception:
            self.audio_ready = False
        self.ensure_ambience_files()
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
        self.bg = "#202124" if dark else "#F2F1EE"
        self.fg = "#F1F1EF" if dark else "#292A2D"
        self.card = "#303135" if dark else "#E1E1DF"
        self.configure(bg=self.bg)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.fg)
        style.configure("TButton", padding=8)

        top = ttk.Frame(self); top.pack(fill="x", padx=22, pady=18)
        left = ttk.Frame(top); left.pack(side="left", fill="x", expand=True)
        tk.Button(left, text="＋", width=3, command=self.new_menu, bg="#3C3D40", fg="#F5F5F3", activebackground="#55575B", relief="flat", font=("TkDefaultFont", 13, "bold")).pack(anchor="w")
        quote = QUOTES[int(time.time()) % len(QUOTES)]
        localized = quote.get(self.data["language"], quote["en"])
        quote_text = f'“{localized}”'
        if self.data["language"] != "English": quote_text += f'\n“{quote["en"]}”'
        quote_text += f'\n— {quote["source"]}'
        ttk.Label(left, text=quote_text, font=("TkDefaultFont", 9), wraplength=430, justify="left").pack(anchor="w", pady=(8, 0))
        ttk.Label(top, text="✦ BellCat", font=("TkDefaultFont", 20, "bold"), foreground=self.fg).pack(side="right")
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
        audio = ttk.Frame(self.content); audio.pack(pady=6)
        self.ambience_button = ttk.Button(audio, text="▶", width=3, command=self.toggle_ambience)
        self.ambience_button.pack(side="left", padx=5)
        self.ambience_var = tk.StringVar(value=AMBIENCE_NAMES.get(self.data.get("ambience", "ocean"), "Ocean Waves"))
        picker = ttk.Combobox(audio, textvariable=self.ambience_var, values=list(AMBIENCE_NAMES.values())[:-1] + (["My Music"] if self.custom_music else []), state="readonly", width=18)
        picker.pack(side="left", padx=5); picker.bind("<<ComboboxSelected>>", self.change_ambience)
        ttk.Button(audio, text="♫ +", command=self.choose_music).pack(side="left", padx=5)
        self.draw_ring()

    def ensure_ambience_files(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for kind in ("ocean", "wind", "rain", "rainforest"):
            path = CONFIG_DIR / f"{kind}.wav"
            if path.exists(): continue
            rate, duration = 22050, 10
            previous = 0.0
            frames = bytearray()
            for frame in range(rate * duration):
                t = frame / rate
                white = random.uniform(-1, 1)
                previous = previous * 0.985 + white * 0.015
                if kind == "ocean": sample = (white * .10 + previous * .8) * (.3 + .7 * (math.sin(t * .42) + 1) / 2)
                elif kind == "wind": sample = previous * (.35 + .25 * math.sin(t * .31))
                elif kind == "rain": sample = white * .13 + (random.uniform(.2, .6) if random.random() > .989 else 0)
                else: sample = previous * .2 + math.sin(t * 2 * math.pi * (1900 + 450 * math.sin(t * 3.1))) * max(0, math.sin(t * .73)) ** 18 * .16
                value = max(-32767, min(32767, int(sample * 22000)))
                frames.extend(struct.pack("<hh", value, int(value * .96)))
            with wave.open(str(path), "wb") as output:
                output.setnchannels(2); output.setsampwidth(2); output.setframerate(rate); output.writeframes(frames)

    def toggle_ambience(self):
        if not self.audio_ready: messagebox.showerror(APP_NAME, "Audio output is unavailable.", parent=self); return
        if self.ambience_playing:
            pygame.mixer.music.pause(); self.ambience_playing = False; self.ambience_button.configure(text="▶")
        else:
            kind = self.data.get("ambience", "ocean")
            path = self.custom_music if kind == "custom" else CONFIG_DIR / f"{kind}.wav"
            try:
                pygame.mixer.music.load(str(path)); pygame.mixer.music.set_volume(.38); pygame.mixer.music.play(-1)
                self.ambience_playing = True; self.ambience_button.configure(text="Ⅱ")
            except Exception as error: messagebox.showerror(APP_NAME, str(error), parent=self)

    def change_ambience(self, _event=None):
        reverse = {value: key for key, value in AMBIENCE_NAMES.items()}
        self.data["ambience"] = reverse[self.ambience_var.get()]; save_config(self.data)
        was_playing = self.ambience_playing
        if was_playing: pygame.mixer.music.stop(); self.ambience_playing = False; self.toggle_ambience()

    def choose_music(self):
        path = filedialog.askopenfilename(parent=self, filetypes=[("Audio", "*.mp3 *.wav *.ogg *.flac"), ("All files", "*.*")])
        if not path: return
        self.custom_music = Path(path); self.data["ambience"] = "custom"; save_config(self.data); self.show_timer()

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
        colors = ["#4B4D51", "#A7A9AD", "#D1CEC6", "#6E7074", "#B9BBC0"]
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
