import SwiftUI

enum AppLanguage: String, CaseIterable, Identifiable {
    case zhHans, en, ja, es, fr, ar, ko

    var id: Self { self }
    var nativeName: String {
        switch self {
        case .zhHans: return "中文"
        case .en: return "English"
        case .ja: return "日本語"
        case .es: return "Español"
        case .fr: return "Français"
        case .ar: return "العربية"
        case .ko: return "한국어"
        }
    }
    var locale: Locale {
        Locale(identifier: [
            .zhHans: "zh-Hans", .en: "en", .ja: "ja", .es: "es",
            .fr: "fr", .ar: "ar", .ko: "ko"
        ][self]!)
    }
    var layoutDirection: LayoutDirection { self == .ar ? .rightToLeft : .leftToRight }

    static var saved: AppLanguage {
        guard let raw = UserDefaults.standard.string(forKey: LanguageManager.defaultsKey),
              let language = AppLanguage(rawValue: raw) else { return .zhHans }
        return language
    }
}

@MainActor
final class LanguageManager: ObservableObject {
    nonisolated static let defaultsKey = "bellcat.language.v1"
    @Published private(set) var selected = AppLanguage.saved

    func select(_ language: AppLanguage) {
        selected = language
        UserDefaults.standard.set(language.rawValue, forKey: Self.defaultsKey)
    }
}

enum LKey {
    case work, rest, focusWork, takeBreak, focusComplete, restComplete, breakMinutes, readyToStart
    case notification, alarm, onTime, advanceDays, advanceHours, advanceMinutes, eventNotificationBody
    case timer, reminders, focusSubtitle, reminderSubtitle, feature, settings, focusing, relax, reset
    case pause, start, completedRounds, custom, language
    case reminderItems, newReminder, quickAddReminder, addReminderNow, reminderTime, noReminders, reminderExample, reminderDetail, expired
    case minutes, hours, days, airportDefault, reminderName, eventDateTime, advance, unit, alertMethod
    case willRemind, alarmDescription, notificationDescription, futureTimeError, cancel, saveReminder
    case taskName, workMinutes, restMinutes, endSound, sound, customFile, chooseAudio, removeCustom, previewSixSeconds, stopPreview, done
    case newItem, routine, createTask, taskDuration, addStage, stageName, other, savedTasks
    case theme, appearance, systemMode, lightMode, darkMode, backgroundImage, chooseBackground
    case removeBackground, backgroundOpacity, clickDragHint, stageColor, customColor, add, delete, quoteBy
    case whiteNoise, ocean, wind, rain, rainforest, chooseMusic, customMusic
}

enum L10n {
    static func text(_ key: LKey, _ language: AppLanguage = .saved, _ arguments: CVarArg...) -> String {
        let format = strings[language]?[key] ?? strings[.en]![key]!
        return String(format: format, locale: language.locale, arguments: arguments)
    }

    static func date(_ date: Date, _ language: AppLanguage, long: Bool = true) -> String {
        if long {
            return date.formatted(Date.FormatStyle(date: .long, time: .shortened).locale(language.locale))
        }
        return date.formatted(Date.FormatStyle(date: .abbreviated, time: .shortened).locale(language.locale))
    }

    private static let strings: [AppLanguage: [LKey: String]] = [
        .zhHans: [
            .work: "工作", .rest: "休息", .focusWork: "专注工作", .takeBreak: "休息一下",
            .focusComplete: "专注完成", .restComplete: "休息结束", .breakMinutes: "该休息 %d 分钟了。",
            .readyToStart: "准备开始：%@", .notification: "通知", .alarm: "闹钟", .onTime: "准时",
            .advanceDays: "提前 %d 天", .advanceHours: "提前 %d 小时", .advanceMinutes: "提前 %d 分钟",
            .eventNotificationBody: "事件时间：%@（%@）", .timer: "专注", .reminders: "日程提醒",
            .focusSubtitle: "给专注留一段安静的时间", .reminderSubtitle: "重要的事，提前准备", .feature: "功能",
            .settings: "设置", .focusing: "专注中", .relax: "放松一下", .reset: "重置", .pause: "暂停",
            .start: "开始", .completedRounds: "已完成 %d 轮", .custom: "自定义", .language: "语言",
            .reminderItems: "提醒事项", .newReminder: "新建提醒", .quickAddReminder: "一键添加提醒", .addReminderNow: "添加提醒", .reminderTime: "提醒时间", .noReminders: "还没有提醒",
            .reminderExample: "例如：9 月 18 日乘飞机，提前 3 小时到浦东机场",
            .reminderDetail: "%@提醒 · %@", .expired: "已过期", .minutes: "分钟", .hours: "小时", .days: "天",
            .airportDefault: "到浦东机场", .reminderName: "提醒名称", .eventDateTime: "事件日期与时间",
            .advance: "提前", .unit: "单位", .alertMethod: "提醒方式", .willRemind: "将在 %@ 提醒",
            .alarmDescription: "闹钟模式会每隔 15 秒响一次，共 3 次。", .notificationDescription: "通知模式会发送一次系统通知。",
            .futureTimeError: "提醒时间必须晚于现在。", .cancel: "取消", .saveReminder: "保存提醒",
            .taskName: "任务名称", .workMinutes: "工作：%d 分钟", .restMinutes: "休息：%d 分钟",
            .endSound: "结束提示音", .sound: "提示音", .customFile: "自定义：%@", .chooseAudio: "选择音频文件…",
            .removeCustom: "移除自定义", .previewSixSeconds: "试听 6 秒", .stopPreview: "停止试听", .done: "完成"
            , .newItem: "新建", .routine: "任务", .createTask: "创建任务", .taskDuration: "时长：%d 分钟",
            .addStage: "添加阶段", .stageName: "阶段名称", .other: "其他", .savedTasks: "已保存任务",
            .theme: "主题", .appearance: "外观", .systemMode: "跟随系统", .lightMode: "浅色", .darkMode: "深色",
            .backgroundImage: "背景图片", .chooseBackground: "选择背景图片…", .removeBackground: "移除背景",
            .backgroundOpacity: "背景不透明度：%d%%", .clickDragHint: "点击阶段设置颜色，拖动圆点调整时间", .stageColor: "阶段颜色", .customColor: "自定义颜色", .add: "添加", .delete: "删除", .quoteBy: "— %@"
            , .whiteNoise: "白噪声", .ocean: "海浪", .wind: "风声", .rain: "雨声", .rainforest: "热带雨林鸟鸣", .chooseMusic: "选择音乐…", .customMusic: "我的音乐"
        ],
        .en: [
            .work: "Work", .rest: "Break", .focusWork: "Focus work", .takeBreak: "Take a break",
            .focusComplete: "Focus complete", .restComplete: "Break over", .breakMinutes: "Time for a %d-minute break.",
            .readyToStart: "Ready to start: %@", .notification: "Notification", .alarm: "Alarm", .onTime: "On time",
            .advanceDays: "%d day(s) early", .advanceHours: "%d hour(s) early", .advanceMinutes: "%d minute(s) early",
            .eventNotificationBody: "Event: %@ (%@)", .timer: "Focus", .reminders: "Reminders",
            .focusSubtitle: "Make quiet time for focus", .reminderSubtitle: "Prepare early for what matters", .feature: "Feature",
            .settings: "Settings", .focusing: "Focusing", .relax: "Take it easy", .reset: "Reset", .pause: "Pause",
            .start: "Start", .completedRounds: "%d round(s) completed", .custom: "Custom", .language: "Language",
            .reminderItems: "Reminders", .newReminder: "New Reminder", .quickAddReminder: "Quick Add Reminder", .addReminderNow: "Add Reminder", .reminderTime: "Reminder time", .noReminders: "No reminders yet",
            .reminderExample: "Example: a Sep 18 flight, arrive at Pudong Airport 3 hours early",
            .reminderDetail: "%@ · %@", .expired: "Expired", .minutes: "Minutes", .hours: "Hours", .days: "Days",
            .airportDefault: "Arrive at Pudong Airport", .reminderName: "Reminder name", .eventDateTime: "Event date and time",
            .advance: "Early by", .unit: "Unit", .alertMethod: "Alert type", .willRemind: "Reminder at %@",
            .alarmDescription: "Alarm mode sounds 3 times, 15 seconds apart.", .notificationDescription: "Notification mode sends one system notification.",
            .futureTimeError: "The reminder time must be in the future.", .cancel: "Cancel", .saveReminder: "Save Reminder",
            .taskName: "Task name", .workMinutes: "Work: %d min", .restMinutes: "Break: %d min",
            .endSound: "End sound", .sound: "Sound", .customFile: "Custom: %@", .chooseAudio: "Choose Audio File…",
            .removeCustom: "Remove Custom Sound", .previewSixSeconds: "Preview 6s", .stopPreview: "Stop Preview", .done: "Done"
            , .newItem: "New", .routine: "Task", .createTask: "Create Task", .taskDuration: "Duration: %d min",
            .addStage: "Add Stage", .stageName: "Stage name", .other: "Other", .savedTasks: "Saved Tasks",
            .theme: "Theme", .appearance: "Appearance", .systemMode: "System", .lightMode: "Light", .darkMode: "Dark",
            .backgroundImage: "Background Image", .chooseBackground: "Choose Background…", .removeBackground: "Remove Background",
            .backgroundOpacity: "Background opacity: %d%%", .clickDragHint: "Click a stage for color; drag the dot to seek", .stageColor: "Stage color", .customColor: "Custom color", .add: "Add", .delete: "Delete", .quoteBy: "— %@"
            , .whiteNoise: "White Noise", .ocean: "Ocean Waves", .wind: "Wind", .rain: "Rain", .rainforest: "Rainforest Birds", .chooseMusic: "Choose Music…", .customMusic: "My Music"
        ],
        .ja: [
            .work: "作業", .rest: "休憩", .focusWork: "集中作業", .takeBreak: "ひと休み",
            .focusComplete: "集中時間が終了", .restComplete: "休憩が終了", .breakMinutes: "%d分間休憩しましょう。",
            .readyToStart: "開始しましょう：%@", .notification: "通知", .alarm: "アラーム", .onTime: "時間どおり",
            .advanceDays: "%d日前", .advanceHours: "%d時間前", .advanceMinutes: "%d分前",
            .eventNotificationBody: "予定時刻：%@（%@）", .timer: "集中", .reminders: "リマインダー",
            .focusSubtitle: "集中するための静かな時間", .reminderSubtitle: "大切な予定に早めの準備を", .feature: "機能",
            .settings: "設定", .focusing: "集中中", .relax: "リラックス", .reset: "リセット", .pause: "一時停止",
            .start: "開始", .completedRounds: "%dセット完了", .custom: "カスタム", .language: "言語",
            .reminderItems: "リマインダー", .newReminder: "新規リマインダー", .quickAddReminder: "かんたんリマインダー", .addReminderNow: "リマインダーを追加", .reminderTime: "通知時刻", .noReminders: "リマインダーはありません",
            .reminderExample: "例：9月18日のフライト、3時間前に浦東空港へ",
            .reminderDetail: "%@ · %@", .expired: "期限切れ", .minutes: "分", .hours: "時間", .days: "日",
            .airportDefault: "浦東空港に到着", .reminderName: "リマインダー名", .eventDateTime: "予定日時",
            .advance: "事前通知", .unit: "単位", .alertMethod: "通知方法", .willRemind: "%@に通知します",
            .alarmDescription: "アラームは15秒間隔で3回鳴ります。", .notificationDescription: "システム通知を1回送信します。",
            .futureTimeError: "通知時刻は現在より後にしてください。", .cancel: "キャンセル", .saveReminder: "保存",
            .taskName: "タスク名", .workMinutes: "作業：%d分", .restMinutes: "休憩：%d分",
            .endSound: "終了音", .sound: "サウンド", .customFile: "カスタム：%@", .chooseAudio: "音声ファイルを選択…",
            .removeCustom: "カスタム音を削除", .previewSixSeconds: "6秒試聴", .stopPreview: "試聴を停止", .done: "完了"
            , .newItem: "新規", .routine: "タスク", .createTask: "タスクを作成", .taskDuration: "時間：%d分",
            .addStage: "ステージを追加", .stageName: "ステージ名", .other: "その他", .savedTasks: "保存済みタスク",
            .theme: "テーマ", .appearance: "外観", .systemMode: "システム", .lightMode: "ライト", .darkMode: "ダーク",
            .backgroundImage: "背景画像", .chooseBackground: "背景を選択…", .removeBackground: "背景を削除",
            .backgroundOpacity: "背景の不透明度：%d%%", .clickDragHint: "ステージで色を設定、点をドラッグして時間を調整", .stageColor: "ステージ色", .customColor: "カスタム色", .add: "追加", .delete: "削除", .quoteBy: "— %@"
        ],
        .es: [
            .work: "Trabajo", .rest: "Descanso", .focusWork: "Trabajo enfocado", .takeBreak: "Tómate un descanso",
            .focusComplete: "Sesión completada", .restComplete: "Descanso terminado", .breakMinutes: "Es hora de descansar %d minutos.",
            .readyToStart: "Listo para empezar: %@", .notification: "Notificación", .alarm: "Alarma", .onTime: "A la hora",
            .advanceDays: "%d día(s) antes", .advanceHours: "%d hora(s) antes", .advanceMinutes: "%d minuto(s) antes",
            .eventNotificationBody: "Evento: %@ (%@)", .timer: "Enfoque", .reminders: "Recordatorios",
            .focusSubtitle: "Reserva un momento tranquilo para concentrarte", .reminderSubtitle: "Prepárate con tiempo para lo importante", .feature: "Función",
            .settings: "Ajustes", .focusing: "Concentrándote", .relax: "Relájate", .reset: "Reiniciar", .pause: "Pausar",
            .start: "Iniciar", .completedRounds: "%d ronda(s) completada(s)", .custom: "Personalizado", .language: "Idioma",
            .reminderItems: "Recordatorios", .newReminder: "Nuevo recordatorio", .quickAddReminder: "Añadir recordatorio rápido", .addReminderNow: "Añadir recordatorio", .reminderTime: "Hora del recordatorio", .noReminders: "Aún no hay recordatorios",
            .reminderExample: "Ejemplo: vuelo el 18 de septiembre; llegar a Pudong 3 horas antes",
            .reminderDetail: "%@ · %@", .expired: "Vencido", .minutes: "Minutos", .hours: "Horas", .days: "Días",
            .airportDefault: "Llegar al aeropuerto de Pudong", .reminderName: "Nombre", .eventDateTime: "Fecha y hora del evento",
            .advance: "Anticipación", .unit: "Unidad", .alertMethod: "Tipo de aviso", .willRemind: "Aviso a las %@",
            .alarmDescription: "La alarma suena 3 veces, cada 15 segundos.", .notificationDescription: "Se enviará una notificación del sistema.",
            .futureTimeError: "El aviso debe ser en el futuro.", .cancel: "Cancelar", .saveReminder: "Guardar",
            .taskName: "Nombre de la tarea", .workMinutes: "Trabajo: %d min", .restMinutes: "Descanso: %d min",
            .endSound: "Sonido final", .sound: "Sonido", .customFile: "Personalizado: %@", .chooseAudio: "Elegir archivo de audio…",
            .removeCustom: "Quitar sonido", .previewSixSeconds: "Probar 6 s", .stopPreview: "Detener prueba", .done: "Listo"
            , .newItem: "Nuevo", .routine: "Tarea", .createTask: "Crear tarea", .taskDuration: "Duración: %d min",
            .addStage: "Añadir etapa", .stageName: "Nombre de etapa", .other: "Otro", .savedTasks: "Tareas guardadas",
            .theme: "Tema", .appearance: "Apariencia", .systemMode: "Sistema", .lightMode: "Claro", .darkMode: "Oscuro",
            .backgroundImage: "Imagen de fondo", .chooseBackground: "Elegir fondo…", .removeBackground: "Quitar fondo",
            .backgroundOpacity: "Opacidad del fondo: %d%%", .clickDragHint: "Pulsa una etapa para el color; arrastra el punto para ajustar", .stageColor: "Color de etapa", .customColor: "Color personalizado", .add: "Añadir", .delete: "Eliminar", .quoteBy: "— %@"
        ],
        .fr: [
            .work: "Travail", .rest: "Pause", .focusWork: "Travail concentré", .takeBreak: "Faites une pause",
            .focusComplete: "Session terminée", .restComplete: "Pause terminée", .breakMinutes: "C'est l'heure d'une pause de %d minutes.",
            .readyToStart: "Prêt à commencer : %@", .notification: "Notification", .alarm: "Alarme", .onTime: "À l'heure",
            .advanceDays: "%d jour(s) avant", .advanceHours: "%d heure(s) avant", .advanceMinutes: "%d minute(s) avant",
            .eventNotificationBody: "Événement : %@ (%@)", .timer: "Concentration", .reminders: "Rappels",
            .focusSubtitle: "Un moment calme pour se concentrer", .reminderSubtitle: "Préparez à l'avance ce qui compte", .feature: "Fonction",
            .settings: "Réglages", .focusing: "Concentration", .relax: "Détendez-vous", .reset: "Réinitialiser", .pause: "Pause",
            .start: "Démarrer", .completedRounds: "%d cycle(s) terminé(s)", .custom: "Personnalisé", .language: "Langue",
            .reminderItems: "Rappels", .newReminder: "Nouveau rappel", .quickAddReminder: "Ajouter un rappel rapide", .addReminderNow: "Ajouter le rappel", .reminderTime: "Heure du rappel", .noReminders: "Aucun rappel",
            .reminderExample: "Exemple : vol le 18 septembre, arriver à Pudong 3 heures avant",
            .reminderDetail: "%@ · %@", .expired: "Expiré", .minutes: "Minutes", .hours: "Heures", .days: "Jours",
            .airportDefault: "Arriver à l'aéroport de Pudong", .reminderName: "Nom du rappel", .eventDateTime: "Date et heure",
            .advance: "Anticipation", .unit: "Unité", .alertMethod: "Type d'alerte", .willRemind: "Rappel à %@",
            .alarmDescription: "L'alarme sonne 3 fois à 15 secondes d'intervalle.", .notificationDescription: "Une notification système sera envoyée.",
            .futureTimeError: "L'heure du rappel doit être dans le futur.", .cancel: "Annuler", .saveReminder: "Enregistrer",
            .taskName: "Nom de la tâche", .workMinutes: "Travail : %d min", .restMinutes: "Pause : %d min",
            .endSound: "Son de fin", .sound: "Son", .customFile: "Personnalisé : %@", .chooseAudio: "Choisir un fichier audio…",
            .removeCustom: "Supprimer le son", .previewSixSeconds: "Écouter 6 s", .stopPreview: "Arrêter l’écoute", .done: "Terminé"
            , .newItem: "Nouveau", .routine: "Tâche", .createTask: "Créer une tâche", .taskDuration: "Durée : %d min",
            .addStage: "Ajouter une étape", .stageName: "Nom de l’étape", .other: "Autre", .savedTasks: "Tâches enregistrées",
            .theme: "Thème", .appearance: "Apparence", .systemMode: "Système", .lightMode: "Clair", .darkMode: "Sombre",
            .backgroundImage: "Image d’arrière-plan", .chooseBackground: "Choisir un arrière-plan…", .removeBackground: "Supprimer l’arrière-plan",
            .backgroundOpacity: "Opacité du fond : %d%%", .clickDragHint: "Cliquez sur une étape pour sa couleur ; glissez le point", .stageColor: "Couleur de l’étape", .customColor: "Couleur personnalisée", .add: "Ajouter", .delete: "Supprimer", .quoteBy: "— %@"
        ],
        .ar: [
            .work: "عمل", .rest: "استراحة", .focusWork: "عمل بتركيز", .takeBreak: "خذ استراحة",
            .focusComplete: "اكتمل التركيز", .restComplete: "انتهت الاستراحة", .breakMinutes: "حان وقت استراحة لمدة %d دقيقة.",
            .readyToStart: "جاهز للبدء: %@", .notification: "إشعار", .alarm: "منبّه", .onTime: "في الموعد",
            .advanceDays: "قبل %d يوم", .advanceHours: "قبل %d ساعة", .advanceMinutes: "قبل %d دقيقة",
            .eventNotificationBody: "موعد الحدث: %@ (%@)", .timer: "تركيز", .reminders: "التذكيرات",
            .focusSubtitle: "وقت هادئ للتركيز", .reminderSubtitle: "استعد مبكرًا لما يهم", .feature: "الميزة",
            .settings: "الإعدادات", .focusing: "جارٍ التركيز", .relax: "استرخِ", .reset: "إعادة ضبط", .pause: "إيقاف مؤقت",
            .start: "ابدأ", .completedRounds: "اكتملت %d جولة", .custom: "مخصص", .language: "اللغة",
            .reminderItems: "التذكيرات", .newReminder: "تذكير جديد", .quickAddReminder: "إضافة تذكير سريع", .addReminderNow: "إضافة التذكير", .reminderTime: "وقت التذكير", .noReminders: "لا توجد تذكيرات",
            .reminderExample: "مثال: رحلة في 18 سبتمبر، الوصول إلى مطار بودونغ قبل 3 ساعات",
            .reminderDetail: "%@ · %@", .expired: "منتهي", .minutes: "دقائق", .hours: "ساعات", .days: "أيام",
            .airportDefault: "الوصول إلى مطار بودونغ", .reminderName: "اسم التذكير", .eventDateTime: "تاريخ ووقت الحدث",
            .advance: "التذكير قبل", .unit: "الوحدة", .alertMethod: "نوع التنبيه", .willRemind: "سيتم التذكير في %@",
            .alarmDescription: "يرن المنبّه 3 مرات بفاصل 15 ثانية.", .notificationDescription: "سيتم إرسال إشعار نظام واحد.",
            .futureTimeError: "يجب أن يكون وقت التذكير في المستقبل.", .cancel: "إلغاء", .saveReminder: "حفظ التذكير",
            .taskName: "اسم المهمة", .workMinutes: "العمل: %d دقيقة", .restMinutes: "الاستراحة: %d دقيقة",
            .endSound: "صوت الانتهاء", .sound: "الصوت", .customFile: "مخصص: %@", .chooseAudio: "اختيار ملف صوتي…",
            .removeCustom: "إزالة الصوت", .previewSixSeconds: "معاينة 6 ثوانٍ", .stopPreview: "إيقاف المعاينة", .done: "تم"
            , .newItem: "جديد", .routine: "مهمة", .createTask: "إنشاء مهمة", .taskDuration: "المدة: %d دقيقة",
            .addStage: "إضافة مرحلة", .stageName: "اسم المرحلة", .other: "أخرى", .savedTasks: "المهام المحفوظة",
            .theme: "السمة", .appearance: "المظهر", .systemMode: "النظام", .lightMode: "فاتح", .darkMode: "داكن",
            .backgroundImage: "صورة الخلفية", .chooseBackground: "اختيار خلفية…", .removeBackground: "إزالة الخلفية",
            .backgroundOpacity: "عتامة الخلفية: %d%%", .clickDragHint: "انقر على مرحلة للون، واسحب النقطة لضبط الوقت", .stageColor: "لون المرحلة", .customColor: "لون مخصص", .add: "إضافة", .delete: "حذف", .quoteBy: "— %@"
        ],
        .ko: [
            .work: "작업", .rest: "휴식", .focusWork: "집중 작업", .takeBreak: "잠시 쉬기",
            .focusComplete: "집중 완료", .restComplete: "휴식 종료", .breakMinutes: "%d분 동안 쉬어갈 시간입니다.",
            .readyToStart: "시작할 준비: %@", .notification: "알림", .alarm: "알람", .onTime: "정시에",
            .advanceDays: "%d일 전", .advanceHours: "%d시간 전", .advanceMinutes: "%d분 전",
            .eventNotificationBody: "일정 시간: %@ (%@)", .timer: "집중", .reminders: "일정 알림",
            .focusSubtitle: "집중을 위한 조용한 시간", .reminderSubtitle: "중요한 일을 미리 준비하세요", .feature: "기능",
            .settings: "설정", .focusing: "집중 중", .relax: "휴식하세요", .reset: "초기화", .pause: "일시 정지",
            .start: "시작", .completedRounds: "%d회 완료", .custom: "사용자 지정", .language: "언어",
            .reminderItems: "알림 목록", .newReminder: "새 알림", .quickAddReminder: "빠른 알림 추가", .addReminderNow: "알림 추가", .reminderTime: "알림 시간", .noReminders: "알림이 없습니다",
            .reminderExample: "예: 9월 18일 항공편, 3시간 전 푸둥 공항 도착",
            .reminderDetail: "%@ · %@", .expired: "만료됨", .minutes: "분", .hours: "시간", .days: "일",
            .airportDefault: "푸둥 공항 도착", .reminderName: "알림 이름", .eventDateTime: "일정 날짜 및 시간",
            .advance: "미리 알림", .unit: "단위", .alertMethod: "알림 방식", .willRemind: "%@에 알림",
            .alarmDescription: "알람이 15초 간격으로 3번 울립니다.", .notificationDescription: "시스템 알림을 한 번 보냅니다.",
            .futureTimeError: "알림 시간은 현재보다 나중이어야 합니다.", .cancel: "취소", .saveReminder: "알림 저장",
            .taskName: "작업 이름", .workMinutes: "작업: %d분", .restMinutes: "휴식: %d분",
            .endSound: "종료음", .sound: "소리", .customFile: "사용자 지정: %@", .chooseAudio: "오디오 파일 선택…",
            .removeCustom: "사용자 지정 소리 제거", .previewSixSeconds: "6초 미리듣기", .stopPreview: "미리듣기 중지", .done: "완료"
            , .newItem: "새로 만들기", .routine: "작업", .createTask: "작업 만들기", .taskDuration: "시간: %d분",
            .addStage: "단계 추가", .stageName: "단계 이름", .other: "기타", .savedTasks: "저장된 작업",
            .theme: "테마", .appearance: "화면 모드", .systemMode: "시스템", .lightMode: "라이트", .darkMode: "다크",
            .backgroundImage: "배경 이미지", .chooseBackground: "배경 선택…", .removeBackground: "배경 제거",
            .backgroundOpacity: "배경 불투명도: %d%%", .clickDragHint: "단계를 눌러 색상을 설정하고 점을 끌어 시간을 조절하세요", .stageColor: "단계 색상", .customColor: "사용자 색상", .add: "추가", .delete: "삭제", .quoteBy: "— %@"
        ]
    ]
}
