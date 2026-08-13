#!/usr/bin/env python3
"""BellCat cross-platform desktop app for Windows and Linux."""

import json
import math
import os
import platform
import random
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk
import wave
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

import pygame

APP_NAME = "BellCat"
VERSION = "2.5.2"
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home() / ".config")) / "BellCat"
CONFIG_FILE = CONFIG_DIR / "settings.json"
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ASSET_DIR = RESOURCE_DIR if hasattr(sys, "_MEIPASS") else RESOURCE_DIR / "AppResources"
AMBIENCE_DIR = ASSET_DIR / "Ambience"

LANGUAGES = {
    "中文": {"timer": "专注", "reminders": "提醒", "start": "开始", "pause": "暂停", "reset": "重置", "new": "新建", "settings": "设置", "work": "工作", "rest": "休息", "other": "其他", "task": "任务", "minutes": "分钟", "save": "保存", "cancel": "取消", "title": "名称", "date": "日期 YYYY-MM-DD", "clock": "时间 HH:MM", "advance": "提前分钟", "alarm": "闹钟", "notification": "通知", "no_reminders": "还没有提醒", "theme": "主题", "light": "浅色", "dark": "深色", "language": "语言", "add_stage": "添加阶段", "completed": "已完成 {n} 轮", "hint": "点击色段或拖动圆点", "due": "提醒时间到：{title}"},
    "English": {"timer": "Focus", "reminders": "Reminders", "start": "Start", "pause": "Pause", "reset": "Reset", "new": "New", "settings": "Settings", "work": "Work", "rest": "Break", "other": "Other", "task": "Task", "minutes": "minutes", "save": "Save", "cancel": "Cancel", "title": "Name", "date": "Date YYYY-MM-DD", "clock": "Time HH:MM", "advance": "Minutes early", "alarm": "Alarm", "notification": "Notification", "no_reminders": "No reminders yet", "theme": "Theme", "light": "Light", "dark": "Dark", "language": "Language", "add_stage": "Add stage", "completed": "{n} round(s) completed", "hint": "Click a segment or drag the dot", "due": "Reminder: {title}"},
    "日本語": {"timer": "集中", "reminders": "リマインダー", "start": "開始", "pause": "一時停止", "reset": "リセット", "new": "新規", "settings": "設定", "work": "作業", "rest": "休憩", "other": "その他", "task": "タスク", "minutes": "分", "save": "保存", "cancel": "キャンセル", "title": "名前", "date": "日付 YYYY-MM-DD", "clock": "時刻 HH:MM", "advance": "何分前", "alarm": "アラーム", "notification": "通知", "no_reminders": "リマインダーはありません", "theme": "テーマ", "light": "ライト", "dark": "ダーク", "language": "言語", "add_stage": "ステージを追加", "completed": "{n}セット完了", "hint": "セグメントをクリック、または点をドラッグ", "due": "リマインダー：{title}"},
    "Español": {"timer": "Enfoque", "reminders": "Recordatorios", "start": "Iniciar", "pause": "Pausar", "reset": "Reiniciar", "new": "Nuevo", "settings": "Ajustes", "work": "Trabajo", "rest": "Descanso", "other": "Otro", "task": "Tarea", "minutes": "minutos", "save": "Guardar", "cancel": "Cancelar", "title": "Nombre", "date": "Fecha YYYY-MM-DD", "clock": "Hora HH:MM", "advance": "Minutos antes", "alarm": "Alarma", "notification": "Notificación", "no_reminders": "No hay recordatorios", "theme": "Tema", "light": "Claro", "dark": "Oscuro", "language": "Idioma", "add_stage": "Añadir etapa", "completed": "{n} ronda(s) completada(s)", "hint": "Haz clic o arrastra el punto", "due": "Recordatorio: {title}"},
    "Français": {"timer": "Concentration", "reminders": "Rappels", "start": "Démarrer", "pause": "Pause", "reset": "Réinitialiser", "new": "Nouveau", "settings": "Réglages", "work": "Travail", "rest": "Pause", "other": "Autre", "task": "Tâche", "minutes": "minutes", "save": "Enregistrer", "cancel": "Annuler", "title": "Nom", "date": "Date AAAA-MM-JJ", "clock": "Heure HH:MM", "advance": "Minutes avant", "alarm": "Alarme", "notification": "Notification", "no_reminders": "Aucun rappel", "theme": "Thème", "light": "Clair", "dark": "Sombre", "language": "Langue", "add_stage": "Ajouter une étape", "completed": "{n} cycle(s) terminé(s)", "hint": "Cliquez ou faites glisser le point", "due": "Rappel : {title}"},
    "العربية": {"timer": "تركيز", "reminders": "التذكيرات", "start": "ابدأ", "pause": "إيقاف", "reset": "إعادة", "new": "جديد", "settings": "الإعدادات", "work": "عمل", "rest": "استراحة", "other": "أخرى", "task": "مهمة", "minutes": "دقائق", "save": "حفظ", "cancel": "إلغاء", "title": "الاسم", "date": "التاريخ YYYY-MM-DD", "clock": "الوقت HH:MM", "advance": "دقائق قبل", "alarm": "منبّه", "notification": "إشعار", "no_reminders": "لا توجد تذكيرات", "theme": "السمة", "light": "فاتح", "dark": "داكن", "language": "اللغة", "add_stage": "إضافة مرحلة", "completed": "اكتملت {n} جولة", "hint": "انقر أو اسحب النقطة", "due": "تذكير: {title}"},
    "한국어": {"timer": "집중", "reminders": "알림", "start": "시작", "pause": "일시 정지", "reset": "초기화", "new": "새로 만들기", "settings": "설정", "work": "작업", "rest": "휴식", "other": "기타", "task": "작업", "minutes": "분", "save": "저장", "cancel": "취소", "title": "이름", "date": "날짜 YYYY-MM-DD", "clock": "시간 HH:MM", "advance": "미리 알림(분)", "alarm": "알람", "notification": "알림", "no_reminders": "알림이 없습니다", "theme": "테마", "light": "라이트", "dark": "다크", "language": "언어", "add_stage": "단계 추가", "completed": "{n}회 완료", "hint": "단계를 클릭하거나 점을 드래그", "due": "알림: {title}"},
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
    "selected_task": 0, "reminders": [], "ambience": "ocean", "end_sound": "Bell", "app_opacity": 1.0
}

PRESET_TASKS = [
    {"name": "专注工作", "stages": [{"name": "Work", "minutes": 30, "color": "#4B4D51"}, {"name": "Break", "minutes": 3, "color": "#A7A9AD"}]},
    {"name": "专注", "stages": [{"name": "Work", "minutes": 25, "color": "#4B4D51"}, {"name": "Break", "minutes": 5, "color": "#A7A9AD"}]},
    {"name": "课程学习", "stages": [{"name": "Study", "minutes": 40, "color": "#4B4D51"}, {"name": "Break", "minutes": 10, "color": "#A7A9AD"}]},
]

AMBIENCE_NAMES = {"ocean": "Ocean Waves", "wind": "Wind", "rain": "Rain", "rainforest": "Rainforest Birds", "custom": "My Music"}
COLOR_LABELS = {"中文": "阶段颜色", "English": "Stage color", "日本語": "ステージ色", "Español": "Color de etapa", "Français": "Couleur de l’étape", "العربية": "لون المرحلة", "한국어": "단계 색상"}
END_SOUND_LABELS = {
    "中文": ("结束提示音", "试听 6 秒", "停止试听"), "English": ("End sound", "Preview 6s", "Stop preview"),
    "日本語": ("終了音", "6秒試聴", "試聴を停止"), "Español": ("Sonido final", "Probar 6 s", "Detener prueba"),
    "Français": ("Son de fin", "Écouter 6 s", "Arrêter l’écoute"), "العربية": ("صوت الانتهاء", "معاينة 6 ثوانٍ", "إيقاف المعاينة"),
    "한국어": ("종료음", "6초 미리듣기", "미리듣기 중지")
}
EASTER_EGG_MESSAGES = {
    "中文": (["专注爪已上线 🐾", "摸摸猫，继续加油！", "叮！送你一颗专注星 ✦"], "喵！你发现了 BellCat 的秘密 ✦"),
    "English": (["Focus paws activated 🐾", "A tiny cat boost for you!", "Ding! One focus star for you ✦"], "Meow! You found BellCat's secret ✦"),
    "日本語": (["集中モード、肉球で起動 🐾", "猫パワーをどうぞ！", "チン！集中の星をひとつ ✦"], "ニャー！BellCatの秘密を発見 ✦"),
    "Español": (["Patitas de enfoque activadas 🐾", "¡Un impulso gatuno para ti!", "¡Ding! Una estrella de enfoque ✦"], "¡Miau! Descubriste el secreto de BellCat ✦"),
    "Français": (["Pattes de concentration activées 🐾", "Un petit coup de pouce félin !", "Ding ! Une étoile de concentration ✦"], "Miaou ! Vous avez trouvé le secret de BellCat ✦"),
    "العربية": (["تم تفعيل مخالب التركيز 🐾", "دفعة قطط صغيرة لك!", "رنّة! نجمة تركيز لك ✦"], "مياو! لقد اكتشفت سر BellCat ✦"),
    "한국어": (["집중 발바닥 활성화 🐾", "고양이 기운을 받아요!", "딩! 집중 별 하나를 드려요 ✦"], "야옹! BellCat의 비밀을 찾았어요 ✦")
}
QUICK_REMINDER_LABELS = {
    "中文": ("⚡ 一键添加提醒", "详细提醒", "提醒事项", "提醒时间 YYYY-MM-DD HH:MM", "添加提醒"),
    "English": ("⚡ Quick Add Reminder", "Detailed reminder", "Reminder", "Time YYYY-MM-DD HH:MM", "Add Reminder"),
    "日本語": ("⚡ かんたんリマインダー", "詳細設定", "リマインダー", "時刻 YYYY-MM-DD HH:MM", "追加"),
    "Español": ("⚡ Añadir recordatorio rápido", "Recordatorio detallado", "Recordatorio", "Hora YYYY-MM-DD HH:MM", "Añadir"),
    "Français": ("⚡ Ajouter un rappel rapide", "Rappel détaillé", "Rappel", "Heure YYYY-MM-DD HH:MM", "Ajouter"),
    "العربية": ("⚡ إضافة تذكير سريع", "تذكير مفصل", "التذكير", "الوقت YYYY-MM-DD HH:MM", "إضافة"),
    "한국어": ("⚡ 빠른 알림 추가", "상세 알림", "알림 내용", "시간 YYYY-MM-DD HH:MM", "추가")
}


def load_config():
    try:
        data = {**DEFAULT, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    except Exception:
        data = json.loads(json.dumps(DEFAULT))
    for task in data["tasks"]:
        if task.get("name") in ("番茄时钟", "番茄钟"):
            task["name"] = "专注"
    names = {task["name"] for task in data["tasks"]}
    data["tasks"].extend(json.loads(json.dumps(task)) for task in PRESET_TASKS if task["name"] not in names)
    return data


def save_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class BellCat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.ring_trail = []
        self.dragging_ring_handle = False
        self.trail_animation = None
        self.preview_channel = None
        self.preview_stop_job = None
        self.stage_alarm_channel = None
        self.awaiting_stage_advance = False
        self.logo_click_count = 0
        self.logo_animation_jobs = []
        self.logo_particles = []
        self.logo_message = None
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
        self.attributes("-alpha", 1.0)
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
        self.logo_label = tk.Label(top, text="✦ BellCat", font=("TkDefaultFont", 20, "bold"),
                                   fg=self.fg, bg=self.bg, cursor="hand2", padx=4)
        self.logo_label.pack(side="right")
        self.logo_label.bind("<Button-1>", self.trigger_logo_easter_egg)
        ttk.Button(top, text="⚙", width=3, command=self.settings_dialog).pack(side="right", padx=8)

        nav = ttk.Frame(self); nav.pack(pady=4)
        ttk.Button(nav, text=self.lang["timer"], command=self.show_timer).pack(side="left", padx=4)
        ttk.Button(nav, text=self.lang["reminders"], command=self.show_reminders).pack(side="left", padx=4)
        self.content = ttk.Frame(self); self.content.pack(fill="both", expand=True, padx=22, pady=12)
        self.show_timer()

    def trigger_logo_easter_egg(self, _event=None):
        self.logo_click_count += 1
        for job in self.logo_animation_jobs:
            try: self.after_cancel(job)
            except Exception: pass
        self.logo_animation_jobs.clear()
        for particle in self.logo_particles:
            try: particle.destroy()
            except Exception: pass
        self.logo_particles.clear()
        if self.logo_message is not None:
            try: self.logo_message.destroy()
            except Exception: pass

        regular, secret = EASTER_EGG_MESSAGES.get(self.data["language"], EASTER_EGG_MESSAGES["English"])
        message = secret if self.logo_click_count % 5 == 0 else random.choice(regular)
        self.logo_label.configure(text="🐾 BellCat" if self.logo_click_count % 5 == 0 else "✦ BellCat ✦",
                                  font=("TkDefaultFont", 24, "bold"), fg="#C7A760")
        self.logo_message = tk.Label(self, text=message, font=("TkDefaultFont", 10, "bold"),
                                     bg=self.card, fg=self.fg, padx=10, pady=5, relief="flat")
        self.logo_message.place(relx=.77, y=66, anchor="n")

        self.update_idletasks()
        center_x = self.logo_label.winfo_rootx() - self.winfo_rootx() + self.logo_label.winfo_width() / 2
        center_y = self.logo_label.winfo_rooty() - self.winfo_rooty() + self.logo_label.winfo_height() / 2
        vectors = [(-55,-30), (-62,15), (-25,-48), (48,-38), (64,10), (30,42), (-18,45)]
        symbols = ["✦", "🐾", "★", "✦", "🐾", "★", "✦"]
        for symbol in symbols:
            particle = tk.Label(self, text=symbol, font=("TkDefaultFont", 12, "bold"), bg=self.bg, fg="#C7A760")
            particle.place(x=center_x, y=center_y, anchor="center")
            particle.lift(); self.logo_particles.append(particle)
        for frame in range(1, 13):
            self.logo_animation_jobs.append(self.after(frame * 38, lambda step=frame, cx=center_x, cy=center_y, moves=vectors: self.animate_logo_particles(step, cx, cy, moves)))
        self.logo_animation_jobs.append(self.after(180, lambda: self.logo_label.configure(font=("TkDefaultFont", 18, "bold"))))
        self.logo_animation_jobs.append(self.after(360, lambda: self.logo_label.configure(font=("TkDefaultFont", 20, "bold"), fg=self.fg)))
        self.logo_animation_jobs.append(self.after(1800, self.clear_logo_easter_egg))

    def animate_logo_particles(self, step, center_x, center_y, vectors):
        progress = step / 12
        for particle, (dx, dy) in zip(self.logo_particles, vectors):
            if particle.winfo_exists():
                particle.place(x=center_x + dx * progress, y=center_y + dy * progress, anchor="center")
                if step > 8: particle.configure(fg=self.card)

    def clear_logo_easter_egg(self):
        for particle in self.logo_particles:
            try: particle.destroy()
            except Exception: pass
        self.logo_particles.clear()
        if self.logo_message is not None:
            try: self.logo_message.destroy()
            except Exception: pass
            self.logo_message = None
        if hasattr(self, "logo_label") and self.logo_label.winfo_exists():
            self.logo_label.configure(text="✦ BellCat", font=("TkDefaultFont", 20, "bold"), fg=self.fg)

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
        self.canvas.bind("<Button-1>", self.ring_press)
        self.canvas.bind("<B1-Motion>", self.ring_drag)
        self.canvas.bind("<ButtonRelease-1>", self.ring_release)
        controls = ttk.Frame(self.content); controls.pack(pady=8)
        ttk.Button(controls, text=self.lang["reset"], command=self.reset).pack(side="left", padx=6)
        icon_path = ASSET_DIR / "BellCatIcon-1024.png"
        try:
            self.cat_button_image = tk.PhotoImage(file=str(icon_path)).subsample(17, 17)
            self.start_button = tk.Button(controls, image=self.cat_button_image, command=self.toggle,
                                          bg=self.bg, activebackground=self.card, relief="flat", bd=0,
                                          cursor="hand2", padx=4, pady=4)
        except Exception:
            self.start_button = tk.Button(controls, text="🐱", command=self.toggle, bg=self.bg,
                                          activebackground=self.card, relief="flat", font=("TkDefaultFont", 28))
        self.start_button.pack(side="left", padx=8)
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
        for kind, frequencies in {"Bell": (880, 1320), "Chime": (660, 990), "Pulse": (520, 780)}.items():
            path = CONFIG_DIR / f"end_{kind.lower()}.wav"
            if path.exists(): continue
            rate, duration = 22050, 1.5
            frames = bytearray()
            for frame in range(int(rate * duration)):
                t = frame / rate
                envelope = math.exp(-3.4 * (t % .5)) * (1 if t % .5 < .42 else 0)
                sample = sum(math.sin(2 * math.pi * frequency * t) for frequency in frequencies) * .16 * envelope
                value = max(-32767, min(32767, int(sample * 32767)))
                frames.extend(struct.pack("<hh", value, int(value * .96)))
            with wave.open(str(path), "wb") as output:
                output.setnchannels(2); output.setsampwidth(2); output.setframerate(rate); output.writeframes(frames)

    def toggle_ambience(self):
        if not self.audio_ready: messagebox.showerror(APP_NAME, "Audio output is unavailable.", parent=self); return
        if self.ambience_playing:
            pygame.mixer.music.pause(); self.ambience_playing = False; self.ambience_button.configure(text="▶")
        else:
            kind = self.data.get("ambience", "ocean")
            path = self.custom_music if kind == "custom" else AMBIENCE_DIR / f"{kind}.mp3"
            try:
                volumes = {"ocean": .22, "wind": .12, "rain": .18, "rainforest": .16, "custom": .42}
                pygame.mixer.music.load(str(path)); pygame.mixer.music.set_volume(volumes.get(kind, .18)); pygame.mixer.music.play(-1)
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
        now = time.monotonic()
        self.ring_trail = [(f, created) for f, created in self.ring_trail if now - created < .72]
        for index, (trail_fraction, created) in enumerate(self.ring_trail):
            life = max(0, 1 - (now - created) / .72)
            rank = (index + 1) / max(1, len(self.ring_trail))
            trail_theta = trail_fraction * 2 * math.pi - math.pi / 2
            tx, ty = 205 + 167 * math.cos(trail_theta), 205 + 167 * math.sin(trail_theta)
            radius = max(2, int(8 * life * rank))
            color = self.blend_color(self.stage["color"], self.bg, .42 + .58 * life * rank)
            self.canvas.create_oval(tx-radius, ty-radius, tx+radius, ty+radius, fill=color, outline="")
        self.canvas.create_oval(px-10, py-10, px+10, py+10, fill="white", outline=self.stage["color"], width=4)
        self.canvas.create_text(205, 170, text=self.stage["name"], fill=self.stage["color"], font=("TkDefaultFont", 15, "bold"))
        self.canvas.create_text(205, 215, text=f"{self.seconds_left//60:02d}:{self.seconds_left%60:02d}", fill=self.fg, font=("TkDefaultFont", 42, "bold"))
        self.canvas.create_text(205, 260, text=self.lang["hint"], fill="#888888", font=("TkDefaultFont", 10))
        if self.awaiting_stage_advance:
            next_stage = self.task["stages"][(self.stage_index + 1) % len(self.task["stages"])]
            self.canvas.create_text(205, 292, text=f"🐱 → {next_stage['name']}", fill="#A57C35", font=("TkDefaultFont", 11, "bold"))

    def ring_fraction(self, x, y):
        return ((math.atan2(y - 205, x - 205) + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)

    def ring_press(self, event):
        fraction = self.ring_fraction(event.x, event.y)
        current_total = sum(s["minutes"] for s in self.task["stages"]) * 60
        elapsed_before = sum(s["minutes"] * 60 for s in self.task["stages"][:self.stage_index])
        current_fraction = (elapsed_before + self.stage["minutes"] * 60 - self.seconds_left) / max(1, current_total)
        theta = current_fraction * 2 * math.pi - math.pi / 2
        handle_x, handle_y = 205 + 167 * math.cos(theta), 205 + 167 * math.sin(theta)
        if math.hypot(event.x - handle_x, event.y - handle_y) <= 30:
            self.dragging_ring_handle = True
            self.ring_drag(event)
            return
        if 138 <= math.hypot(event.x - 205, event.y - 205) <= 194:
            self.stop_stage_alarm(); self.awaiting_stage_advance = False
            target = fraction * current_total
            cursor = 0
            for index, stage in enumerate(self.task["stages"]):
                cursor += stage["minutes"] * 60
                if target < cursor:
                    self.stage_index = index
                    self.seconds_left = stage["minutes"] * 60
                    self.draw_ring()
                    self.after_idle(self.choose_stage_color)
                    return

    def ring_drag(self, event):
        if not self.dragging_ring_handle: return
        self.stop_stage_alarm(); self.awaiting_stage_advance = False
        fraction = self.ring_fraction(event.x, event.y)
        now = time.monotonic()
        if not self.ring_trail or now - self.ring_trail[-1][1] > .018 or abs(fraction - self.ring_trail[-1][0]) > .004:
            self.ring_trail.append((fraction, now))
            self.ring_trail = self.ring_trail[-24:]
        target = fraction * sum(s["minutes"] for s in self.task["stages"]) * 60
        cursor = 0
        for i, stage in enumerate(self.task["stages"]):
            duration = stage["minutes"] * 60
            if target < cursor + duration:
                self.stage_index = i; self.seconds_left = max(1, int(duration - (target - cursor))); break
            cursor += duration
        self.draw_ring()

    def ring_release(self, _event):
        self.dragging_ring_handle = False
        self.animate_ring_trail()

    def animate_ring_trail(self):
        if self.trail_animation is not None:
            try: self.after_cancel(self.trail_animation)
            except Exception: pass
        self.draw_ring()
        if self.ring_trail:
            self.trail_animation = self.after(16, self.animate_ring_trail)
        else:
            self.trail_animation = None

    def choose_stage_color(self):
        label = COLOR_LABELS.get(self.data["language"], "Stage color")
        chosen = colorchooser.askcolor(color=self.stage["color"], title=f'{self.stage["name"]} · {label}', parent=self)[1]
        if chosen:
            self.stage["color"] = chosen.upper()
            save_config(self.data)
            self.draw_ring()

    @staticmethod
    def blend_color(foreground, background, amount):
        def rgb(value):
            value = value.lstrip("#")
            return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
        try:
            fg, bg = rgb(foreground), rgb(background)
            mixed = tuple(round(bg[i] + (fg[i] - bg[i]) * amount) for i in range(3))
            return "#%02X%02X%02X" % mixed
        except Exception:
            return foreground

    def select_task(self, _event=None):
        self.data["selected_task"] = [t["name"] for t in self.data["tasks"]].index(self.task_var.get())
        save_config(self.data); self.reset(); self.show_timer()

    def toggle(self):
        if self.running:
            self.running = False
            return
        if getattr(self, "cat_is_being_petted", False): return
        if self.awaiting_stage_advance: self.stop_stage_alarm()
        self.cat_is_being_petted = True
        self.start_button.configure(text="☝", compound="top", relief="sunken", padx=8, pady=8)
        self.after(150, lambda: self.start_button.configure(relief="flat", padx=2, pady=2) if self.start_button.winfo_exists() else None)
        self.after(280, lambda: self.start_button.configure(relief="sunken", padx=6, pady=6) if self.start_button.winfo_exists() else None)
        self.after(460, self.finish_cat_pet)

    def finish_cat_pet(self):
        if hasattr(self, "start_button") and self.start_button.winfo_exists():
            self.start_button.configure(text="", compound="none", relief="flat", padx=4, pady=4)
        self.cat_is_being_petted = False
        if self.awaiting_stage_advance:
            self.awaiting_stage_advance = False
            self.stage_index = (self.stage_index + 1) % len(self.task["stages"])
            if self.stage_index == 0:
                self.data["completed"] += 1
                save_config(self.data)
            self.seconds_left = self.stage["minutes"] * 60
        self.running = True
        self.last_tick = time.monotonic()

    def reset(self):
        self.running = False; self.stop_stage_alarm(); self.awaiting_stage_advance = False
        self.stage_index = 0; self.seconds_left = self.stage["minutes"] * 60; self.draw_ring()

    def tick(self):
        if self.running and time.monotonic() - self.last_tick >= 1:
            ticks = int(time.monotonic() - self.last_tick); self.last_tick += ticks
            self.seconds_left -= ticks
            if self.seconds_left <= 0:
                self.seconds_left = 0
                self.running = False
                self.awaiting_stage_advance = True
                self.play_stage_alarm()
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
        quick_label, detailed_label, _, _, _ = QUICK_REMINDER_LABELS.get(self.data["language"], QUICK_REMINDER_LABELS["English"])
        actions = ttk.Frame(self.content); actions.pack(fill="x", pady=6)
        ttk.Button(actions, text=quick_label, command=self.quick_reminder).pack(side="right", padx=(6, 0))
        ttk.Button(actions, text=detailed_label, command=self.new_reminder).pack(side="right")
        if not self.data["reminders"]: ttk.Label(self.content, text=self.lang["no_reminders"], font=("TkDefaultFont", 16)).pack(expand=True); return
        for reminder in sorted(self.data["reminders"], key=lambda r: r["fire"]):
            frame = ttk.Frame(self.content); frame.pack(fill="x", pady=7)
            ttk.Label(frame, text="⏰" if reminder["style"] == "alarm" else "🔔", font=("TkDefaultFont", 18)).pack(side="left")
            ttk.Label(frame, text=f"{reminder['title']}\n{reminder['event'].replace('T', ' ')}", font=("TkDefaultFont", 12)).pack(side="left", padx=10)
            ttk.Button(frame, text="×", command=lambda r=reminder: self.delete_reminder(r)).pack(side="right")

    def quick_reminder(self):
        window = tk.Toplevel(self); window.title(APP_NAME); window.geometry("440x280"); window.transient(self); window.grab_set()
        quick_label, _, item_label, time_label, add_label = QUICK_REMINDER_LABELS.get(self.data["language"], QUICK_REMINDER_LABELS["English"])
        ttk.Label(window, text=quick_label, font=("TkDefaultFont", 16, "bold")).pack(anchor="w", padx=24, pady=(22, 14))
        form = ttk.Frame(window); form.pack(fill="x", padx=24)
        ttk.Label(form, text=item_label).grid(row=0, column=0, sticky="w", pady=6)
        title = ttk.Entry(form, width=34); title.grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=6); title.focus_set()
        ttk.Label(form, text=time_label).grid(row=1, column=0, sticky="w", pady=6)
        when = ttk.Entry(form, width=34)
        when.insert(0, (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"))
        when.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=6)
        style = tk.StringVar(value="notification")
        choices = ttk.Frame(form); choices.grid(row=2, column=1, sticky="w", padx=(12, 0), pady=8)
        ttk.Radiobutton(choices, text=self.lang["notification"], variable=style, value="notification").pack(side="left", padx=(0, 14))
        ttk.Radiobutton(choices, text=self.lang["alarm"], variable=style, value="alarm").pack(side="left")
        form.columnconfigure(1, weight=1)
        def save_quick(_event=None):
            name = title.get().strip()
            try: event = datetime.strptime(when.get().strip(), "%Y-%m-%d %H:%M")
            except Exception: messagebox.showerror(APP_NAME, time_label, parent=window); return
            if not name or event <= datetime.now(): messagebox.showerror(APP_NAME, self.lang["futureTimeError"] if "futureTimeError" in self.lang else time_label, parent=window); return
            self.data["reminders"].append({"title": name, "event": event.isoformat(timespec="minutes"), "fire": event.isoformat(timespec="seconds"), "style": style.get(), "fired": False})
            save_config(self.data); window.destroy(); self.show_reminders()
        ttk.Button(window, text=add_label, command=save_quick).pack(anchor="e", padx=24, pady=20)
        window.bind("<Return>", save_quick)

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

    def bell(self):
        self.stop_end_sound_preview()
        if not self.audio_ready: return
        try: pygame.mixer.Sound(str(CONFIG_DIR / f'end_{self.data.get("end_sound", "Bell").lower()}.wav')).play()
        except Exception: pass

    def play_stage_alarm(self):
        self.stop_end_sound_preview()
        self.stop_stage_alarm()
        if not self.audio_ready: return
        try:
            sound = pygame.mixer.Sound(str(CONFIG_DIR / f'end_{self.data.get("end_sound", "Bell").lower()}.wav'))
            self.stage_alarm_channel = sound.play(loops=-1)
        except Exception: self.stage_alarm_channel = None

    def stop_stage_alarm(self):
        if self.stage_alarm_channel is not None: self.stage_alarm_channel.stop()
        self.stage_alarm_channel = None

    def toggle_end_sound_preview(self):
        if self.preview_channel is not None and self.preview_channel.get_busy():
            self.stop_end_sound_preview(); return
        if not self.audio_ready: return
        try:
            sound = pygame.mixer.Sound(str(CONFIG_DIR / f'end_{self.data.get("end_sound", "Bell").lower()}.wav'))
            self.preview_channel = sound.play(loops=-1)
            self.preview_button.configure(text=END_SOUND_LABELS.get(self.data["language"], END_SOUND_LABELS["English"])[2])
            self.preview_stop_job = self.after(6000, self.stop_end_sound_preview)
        except Exception: pass

    def stop_end_sound_preview(self):
        if self.preview_stop_job is not None:
            try: self.after_cancel(self.preview_stop_job)
            except Exception: pass
            self.preview_stop_job = None
        if self.preview_channel is not None: self.preview_channel.stop()
        self.preview_channel = None
        if hasattr(self, "preview_button") and self.preview_button.winfo_exists():
            self.preview_button.configure(text=END_SOUND_LABELS.get(self.data["language"], END_SOUND_LABELS["English"])[1])

    def settings_dialog(self):
        win = tk.Toplevel(self); win.title(self.lang["settings"]); win.geometry("390x400"); win.transient(self); win.grab_set()
        ttk.Label(win, text=self.lang["language"]).pack(pady=(20,4))
        language = ttk.Combobox(win, values=list(LANGUAGES), state="readonly"); language.set(self.data["language"]); language.pack()
        ttk.Label(win, text=self.lang["theme"]).pack(pady=(18,4))
        theme = ttk.Combobox(win, values=["light", "dark"], state="readonly"); theme.set(self.data["theme"]); theme.pack()
        opacity_labels = {"中文": "背景不透明度", "English": "Background opacity", "日本語": "背景の不透明度", "Español": "Opacidad del fondo", "Français": "Opacité du fond", "العربية": "عتامة الخلفية", "한국어": "배경 불투명도"}
        ttk.Label(win, text=opacity_labels.get(self.data["language"], "Background opacity")).pack(pady=(18, 4))
        opacity = tk.DoubleVar(value=float(self.data.get("app_opacity", 1.0)))
        opacity_value = ttk.Label(win, text=f"{round(opacity.get() * 100)}%")
        opacity_value.pack()
        def update_opacity(value):
            amount = max(0, min(1.0, float(value)))
            opacity_value.configure(text=f"{round(amount * 100)}%")
            self.data["app_opacity"] = amount
            save_config(self.data)
        ttk.Scale(win, from_=0, to=1.0, variable=opacity, command=update_opacity).pack(fill="x", padx=52)
        end_label, preview_label, _ = END_SOUND_LABELS.get(self.data["language"], END_SOUND_LABELS["English"])
        ttk.Label(win, text=end_label).pack(pady=(18,4))
        sound_row = ttk.Frame(win); sound_row.pack()
        end_sound = ttk.Combobox(sound_row, values=["Bell", "Chime", "Pulse"], state="readonly", width=12)
        end_sound.set(self.data.get("end_sound", "Bell")); end_sound.pack(side="left", padx=5)
        def select_end_sound(_event=None):
            self.stop_end_sound_preview(); self.data["end_sound"] = end_sound.get(); save_config(self.data)
        end_sound.bind("<<ComboboxSelected>>", select_end_sound)
        self.preview_button = ttk.Button(sound_row, text=preview_label, command=self.toggle_end_sound_preview)
        self.preview_button.pack(side="left", padx=5)
        def apply():
            self.stop_end_sound_preview(); self.data["language"] = language.get(); self.data["theme"] = theme.get(); self.data["end_sound"] = end_sound.get(); self.data["app_opacity"] = opacity.get(); save_config(self.data)
            self.lang = LANGUAGES[self.data["language"]]; win.destroy(); self.configure_ui()
        win.protocol("WM_DELETE_WINDOW", lambda: (self.stop_end_sound_preview(), win.destroy()))
        ttk.Button(win, text=self.lang["save"], command=apply).pack(pady=22)


if __name__ == "__main__":
    BellCat().mainloop()
