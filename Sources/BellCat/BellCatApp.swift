import SwiftUI
import AppKit
import UniformTypeIdentifiers
import UserNotifications
import AVFoundation

@main
struct BellCatApp: App {
    @NSApplicationDelegateAdaptor(BellCatAppDelegate.self) private var appDelegate
    @StateObject private var timer = FocusTimer()
    @StateObject private var reminders = ReminderStore()
    @StateObject private var language = LanguageManager()
    @StateObject private var theme = ThemeManager()
    @StateObject private var ambience = AmbiencePlayer()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(timer)
                .environmentObject(reminders)
                .environmentObject(language)
                .environmentObject(theme)
                .environmentObject(ambience)
                .environment(\.locale, language.selected.locale)
                .environment(\.layoutDirection, language.selected.layoutDirection)
                .preferredColorScheme(theme.preferredColorScheme)
                .frame(minWidth: 680, minHeight: 650)
        }
        .windowStyle(.hiddenTitleBar)
    }
}

final class BellCatAppDelegate: NSObject, NSApplicationDelegate, UNUserNotificationCenterDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        UNUserNotificationCenter.current().delegate = self
        NotificationAccess.request()
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }
}

enum AmbienceSound: String, CaseIterable, Identifiable {
    case ocean, wind, rain, rainforest, custom
    var id: Self { self }

    func title(_ language: AppLanguage) -> String {
        switch self {
        case .ocean: return L10n.text(.ocean, language)
        case .wind: return L10n.text(.wind, language)
        case .rain: return L10n.text(.rain, language)
        case .rainforest: return L10n.text(.rainforest, language)
        case .custom: return L10n.text(.customMusic, language)
        }
    }
}

@MainActor
final class AmbiencePlayer: ObservableObject {
    @Published var selected: AmbienceSound = .ocean
    @Published private(set) var isPlaying = false
    @Published var customURL: URL?

    private let engine = AVAudioEngine()
    private let node = AVAudioPlayerNode()
    private var filePlayer: AVAudioPlayer?
    private let sampleRate = 44_100.0

    init() {
        engine.attach(node)
        let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 2)!
        engine.connect(node, to: engine.mainMixerNode, format: format)
        engine.mainMixerNode.outputVolume = 0.32
    }

    func toggle() { isPlaying ? pause() : play() }

    func choose(_ sound: AmbienceSound) {
        let wasPlaying = isPlaying
        pause()
        selected = sound
        if wasPlaying { play() }
    }

    func setCustomFile(_ url: URL) {
        customURL = url
        choose(.custom)
    }

    func play() {
        if selected == .custom, let url = customURL {
            do {
                filePlayer = try AVAudioPlayer(contentsOf: url)
                filePlayer?.numberOfLoops = -1
                filePlayer?.volume = 0.45
                filePlayer?.play()
                isPlaying = true
            } catch { isPlaying = false }
            return
        }

        node.stop()
        let buffer = makeBuffer(for: selected)
        node.scheduleBuffer(buffer, at: nil, options: .loops)
        do {
            if !engine.isRunning { try engine.start() }
            node.play()
            isPlaying = true
        } catch { isPlaying = false }
    }

    func pause() {
        node.pause()
        filePlayer?.pause()
        isPlaying = false
    }

    private func makeBuffer(for sound: AmbienceSound) -> AVAudioPCMBuffer {
        let frameCount = AVAudioFrameCount(sampleRate * 12)
        let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 2)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frameCount)!
        buffer.frameLength = frameCount
        var previous: Float = 0

        for frame in 0..<Int(frameCount) {
            let t = Double(frame) / sampleRate
            let white = Float.random(in: -1...1)
            previous = previous * 0.985 + white * 0.015
            var sample: Float
            switch sound {
            case .ocean:
                let swell = Float((sin(t * 0.42) + 1) * 0.5)
                sample = (white * 0.11 + previous * 0.8) * (0.2 + swell * 0.8)
            case .wind:
                let gust = Float(0.35 + 0.3 * sin(t * 0.31) + 0.2 * sin(t * 0.09))
                sample = previous * gust
            case .rain:
                let drop: Float = Float.random(in: 0...1) > 0.985 ? Float.random(in: 0.25...0.75) : 0
                sample = white * 0.16 + drop
            case .rainforest:
                let bird = sin(t * 2 * .pi * (1_900 + 500 * sin(t * 3.1)))
                let gate = pow(max(0, sin(t * 0.73)), 18)
                sample = previous * 0.22 + Float(bird * gate) * 0.18
            case .custom:
                sample = 0
            }
            buffer.floatChannelData?[0][frame] = sample
            buffer.floatChannelData?[1][frame] = sample * 0.96
        }
        return buffer
    }
}

enum NotificationAccess {
    static func request() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }
}

enum StageKind: String, Codable, CaseIterable, Identifiable {
    case work, rest, other
    var id: Self { self }

    func title(_ language: AppLanguage) -> String {
        switch self {
        case .work: return L10n.text(.work, language)
        case .rest: return L10n.text(.rest, language)
        case .other: return L10n.text(.other, language)
        }
    }
}

struct TaskStage: Identifiable, Codable, Equatable {
    var id = UUID()
    var kind: StageKind
    var customName = ""
    var minutes: Int
    var colorHex: String

    func title(_ language: AppLanguage) -> String {
        kind == .other && !customName.isEmpty ? customName : kind.title(language)
    }
}

struct FocusRoutine: Identifiable, Codable, Equatable {
    var id = UUID()
    var name: String
    var stages: [TaskStage]
    var totalMinutes: Int { stages.reduce(0) { $0 + $1.minutes } }
}

@MainActor
final class FocusTimer: ObservableObject {
    @Published private(set) var routines: [FocusRoutine] = []
    @Published var selectedRoutineID: UUID
    @Published var currentStageIndex = 0
    @Published var secondsLeft = 25 * 60
    @Published var isRunning = false
    @Published var completedRounds = 0
    @Published var soundChoice = "Glass"
    @Published var customSoundURL: URL?
    @Published private(set) var isPreviewingSound = false

    private var ticker: Timer?
    private var previewSound: NSSound?
    private var previewStopWorkItem: DispatchWorkItem?
    private let routinesKey = "bellcat.routines.v2"
    private let selectedKey = "bellcat.selectedRoutine.v2"

    init() {
        let presets = Self.presetRoutines()
        let loadedRoutines: [FocusRoutine]
        if let data = UserDefaults.standard.data(forKey: routinesKey),
           let saved = try? JSONDecoder().decode([FocusRoutine].self, from: data), !saved.isEmpty {
            let monochrome = ["4B4D51", "A7A9AD", "D1CEC6", "6E7074", "B9BBC0", "34363A"]
            loadedRoutines = saved.map { routine in
                var updated = routine
                updated.stages = routine.stages.enumerated().map { index, stage in
                    var updatedStage = stage
                    let legacyColors = ["F3A83B", "58BFA8", "ED6A5A", "7A8EDB", "B67AD9", "5BA6D9"]
                    if legacyColors.contains(stage.colorHex.uppercased()) {
                        updatedStage.colorHex = monochrome[index % monochrome.count]
                    }
                    return updatedStage
                }
                return updated
            }
        } else {
            loadedRoutines = presets
        }
        var merged = loadedRoutines
        for preset in presets where !merged.contains(where: { $0.name == preset.name }) {
            merged.append(preset)
        }
        routines = merged
        if merged.count != loadedRoutines.count, let data = try? JSONEncoder().encode(merged) {
            UserDefaults.standard.set(data, forKey: routinesKey)
        }
        if let raw = UserDefaults.standard.string(forKey: selectedKey),
           let id = UUID(uuidString: raw), merged.contains(where: { $0.id == id }) {
            selectedRoutineID = id
        } else {
            selectedRoutineID = merged[0].id
        }
        let selected = merged.first(where: { $0.id == selectedRoutineID }) ?? merged[0]
        secondsLeft = selected.stages[0].minutes * 60
        NotificationAccess.request()
    }

    deinit { ticker?.invalidate() }

    private static func presetRoutines() -> [FocusRoutine] {
        [
            FocusRoutine(name: "专注工作", stages: [
                TaskStage(kind: .work, minutes: 30, colorHex: "4B4D51"),
                TaskStage(kind: .rest, minutes: 3, colorHex: "A7A9AD")]),
            FocusRoutine(name: "番茄时钟", stages: [
                TaskStage(kind: .work, minutes: 25, colorHex: "4B4D51"),
                TaskStage(kind: .rest, minutes: 5, colorHex: "A7A9AD")]),
            FocusRoutine(name: "课程学习", stages: [
                TaskStage(kind: .work, minutes: 40, colorHex: "4B4D51"),
                TaskStage(kind: .rest, minutes: 10, colorHex: "A7A9AD")])
        ]
    }

    var currentRoutine: FocusRoutine {
        routines.first(where: { $0.id == selectedRoutineID }) ?? routines[0]
    }
    var currentStage: TaskStage {
        let stages = currentRoutine.stages
        return stages[min(currentStageIndex, max(0, stages.count - 1))]
    }
    var remainingText: String { String(format: "%02d:%02d", secondsLeft / 60, secondsLeft % 60) }
    var totalSeconds: Int { max(1, currentRoutine.totalMinutes * 60) }
    var elapsedSeconds: Int {
        let before = currentRoutine.stages.prefix(currentStageIndex).reduce(0) { $0 + $1.minutes * 60 }
        return before + max(0, currentStage.minutes * 60 - secondsLeft)
    }
    var sequenceProgress: Double { min(1, max(0, Double(elapsedSeconds) / Double(totalSeconds))) }

    func startPause() { isRunning ? pause() : start() }
    func start() {
        guard !isRunning else { return }
        isRunning = true
        ticker = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.tick() }
        }
    }
    func pause() {
        isRunning = false
        ticker?.invalidate()
        ticker = nil
    }
    func reset() {
        pause()
        currentStageIndex = 0
        secondsLeft = currentStage.minutes * 60
    }
    func selectRoutine(_ id: UUID) {
        selectedRoutineID = id
        UserDefaults.standard.set(id.uuidString, forKey: selectedKey)
        reset()
    }
    func addRoutine(_ routine: FocusRoutine) {
        routines.append(routine)
        saveRoutines()
        selectRoutine(routine.id)
    }
    func deleteRoutine(_ routine: FocusRoutine) {
        guard routines.count > 1, let index = routines.firstIndex(of: routine) else { return }
        routines.remove(at: index)
        if selectedRoutineID == routine.id { selectRoutine(routines[0].id) }
        saveRoutines()
    }
    func selectStage(_ index: Int) {
        guard currentRoutine.stages.indices.contains(index) else { return }
        currentStageIndex = index
        secondsLeft = currentStage.minutes * 60
    }
    func updateStageColor(_ stageID: UUID, hex: String) {
        guard let routineIndex = routines.firstIndex(where: { $0.id == selectedRoutineID }),
              let stageIndex = routines[routineIndex].stages.firstIndex(where: { $0.id == stageID }) else { return }
        routines[routineIndex].stages[stageIndex].colorHex = hex
        saveRoutines()
    }
    func seek(to fraction: Double) {
        let target = min(totalSeconds - 1, max(0, Int(Double(totalSeconds) * fraction)))
        var cursor = 0
        for (index, stage) in currentRoutine.stages.enumerated() {
            let duration = stage.minutes * 60
            if target < cursor + duration {
                currentStageIndex = index
                secondsLeft = max(1, duration - (target - cursor))
                return
            }
            cursor += duration
        }
    }

    private func tick() {
        if secondsLeft > 1 { secondsLeft -= 1 } else { finishStage() }
    }
    private func finishStage() {
        playAlarm()
        let language = AppLanguage.saved
        let finished = currentStage.title(language)
        let nextIndex = (currentStageIndex + 1) % currentRoutine.stages.count
        if nextIndex == 0 { completedRounds += 1 }
        currentStageIndex = nextIndex
        secondsLeft = currentStage.minutes * 60

        let content = UNMutableNotificationContent()
        content.title = finished
        content.body = L10n.text(.readyToStart, language, currentStage.title(language))
        content.sound = .default
        UNUserNotificationCenter.current().add(
            UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        )
    }
    private func playAlarm() {
        stopSoundPreview()
        configuredEndSound()?.play()
    }
    func toggleSoundPreview() {
        if isPreviewingSound {
            stopSoundPreview()
            return
        }
        guard let sound = configuredEndSound() else { return }
        previewStopWorkItem?.cancel()
        previewSound = sound
        isPreviewingSound = true
        sound.play()
        let stopWork = DispatchWorkItem { [weak self] in
            Task { @MainActor in self?.stopSoundPreview() }
        }
        previewStopWorkItem = stopWork
        DispatchQueue.main.asyncAfter(deadline: .now() + 6, execute: stopWork)
    }
    func stopSoundPreview() {
        previewStopWorkItem?.cancel()
        previewStopWorkItem = nil
        previewSound?.stop()
        previewSound = nil
        isPreviewingSound = false
    }
    private func configuredEndSound() -> NSSound? {
        if soundChoice == "custom", let url = customSoundURL {
            return NSSound(contentsOf: url, byReference: true)
        }
        return NSSound(named: NSSound.Name(soundChoice))
    }
    private func saveRoutines() {
        if let data = try? JSONEncoder().encode(routines) {
            UserDefaults.standard.set(data, forKey: routinesKey)
        }
    }
}

struct ReminderItem: Identifiable, Codable, Equatable {
    enum AlertStyle: String, Codable, CaseIterable, Identifiable {
        case notification, alarm
        var id: Self { self }
    }
    var id = UUID()
    var title: String
    var eventDate: Date
    var advanceMinutes: Int
    var style: AlertStyle
    var isEnabled = true
    var fireDate: Date { eventDate.addingTimeInterval(TimeInterval(-advanceMinutes * 60)) }

    func advanceText(language: AppLanguage) -> String {
        if advanceMinutes == 0 { return L10n.text(.onTime, language) }
        if advanceMinutes % 1440 == 0 { return L10n.text(.advanceDays, language, advanceMinutes / 1440) }
        if advanceMinutes % 60 == 0 { return L10n.text(.advanceHours, language, advanceMinutes / 60) }
        return L10n.text(.advanceMinutes, language, advanceMinutes)
    }
}

@MainActor
final class ReminderStore: ObservableObject {
    @Published private(set) var items: [ReminderItem] = []
    private let defaultsKey = "bellcat.reminders.v2"

    init() {
        NotificationAccess.request()
        load()
        rescheduleAll()
    }
    func add(_ item: ReminderItem) {
        items.append(item)
        items.sort { $0.fireDate < $1.fireDate }
        save(); schedule(item)
    }
    func delete(at offsets: IndexSet) {
        let removed = offsets.map { items[$0] }
        items.remove(atOffsets: offsets)
        removed.forEach(cancel)
        save()
    }
    func setEnabled(_ enabled: Bool, for item: ReminderItem) {
        guard let index = items.firstIndex(where: { $0.id == item.id }) else { return }
        items[index].isEnabled = enabled
        save()
        enabled ? schedule(items[index]) : cancel(items[index])
    }
    func refreshNotificationLanguage() { rescheduleAll() }
    private func load() {
        guard let data = UserDefaults.standard.data(forKey: defaultsKey),
              let decoded = try? JSONDecoder().decode([ReminderItem].self, from: data) else { return }
        items = decoded.sorted { $0.fireDate < $1.fireDate }
    }
    private func save() {
        if let data = try? JSONEncoder().encode(items) { UserDefaults.standard.set(data, forKey: defaultsKey) }
    }
    private func identifiers(for item: ReminderItem) -> [String] {
        (0..<3).map { "bellcat-reminder-\(item.id.uuidString)-\($0)" }
    }
    private func cancel(_ item: ReminderItem) {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: identifiers(for: item))
    }
    private func rescheduleAll() {
        for item in items { cancel(item) }
        for item in items where item.isEnabled && item.fireDate > Date() { schedule(item) }
    }
    private func schedule(_ item: ReminderItem) {
        cancel(item)
        guard item.isEnabled, item.fireDate > Date() else { return }
        let language = AppLanguage.saved
        let repeatCount = item.style == .alarm ? 3 : 1
        for index in 0..<repeatCount {
            let deliveryDate = item.fireDate.addingTimeInterval(TimeInterval(index * 15))
            let content = UNMutableNotificationContent()
            content.title = item.style == .alarm ? "⏰ \(item.title)" : item.title
            content.body = L10n.text(
                .eventNotificationBody, language,
                L10n.date(item.eventDate, language, long: false), item.advanceText(language: language)
            )
            content.sound = .default
            let parts = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute, .second], from: deliveryDate)
            let trigger = UNCalendarNotificationTrigger(dateMatching: parts, repeats: false)
            UNUserNotificationCenter.current().add(
                UNNotificationRequest(identifier: identifiers(for: item)[index], content: content, trigger: trigger)
            )
        }
    }
}

@MainActor
final class ThemeManager: ObservableObject {
    enum Appearance: String, CaseIterable, Identifiable {
        case system, light, dark
        var id: Self { self }
    }
    @Published var appearance: Appearance
    @Published var backgroundOpacity: Double
    @Published private(set) var backgroundURL: URL?
    private let appearanceKey = "bellcat.appearance.v1"
    private let opacityKey = "bellcat.backgroundOpacity.v1"
    private let bookmarkKey = "bellcat.backgroundBookmark.v1"

    init() {
        appearance = Appearance(rawValue: UserDefaults.standard.string(forKey: appearanceKey) ?? "") ?? .system
        let savedOpacity = UserDefaults.standard.object(forKey: opacityKey) as? Double
        backgroundOpacity = savedOpacity ?? 0.32
        loadBackground()
    }
    var preferredColorScheme: ColorScheme? {
        switch appearance { case .system: return nil; case .light: return .light; case .dark: return .dark }
    }
    func setAppearance(_ value: Appearance) {
        appearance = value
        UserDefaults.standard.set(value.rawValue, forKey: appearanceKey)
    }
    func setOpacity(_ value: Double) {
        backgroundOpacity = value
        UserDefaults.standard.set(value, forKey: opacityKey)
    }
    func setBackground(_ url: URL) {
        do {
            let data = try url.bookmarkData(options: .withSecurityScope, includingResourceValuesForKeys: nil, relativeTo: nil)
            UserDefaults.standard.set(data, forKey: bookmarkKey)
            backgroundURL = url
            _ = url.startAccessingSecurityScopedResource()
        } catch { backgroundURL = url }
    }
    func removeBackground() {
        backgroundURL?.stopAccessingSecurityScopedResource()
        backgroundURL = nil
        UserDefaults.standard.removeObject(forKey: bookmarkKey)
    }
    private func loadBackground() {
        guard let data = UserDefaults.standard.data(forKey: bookmarkKey) else { return }
        var stale = false
        if let url = try? URL(resolvingBookmarkData: data, options: [.withSecurityScope, .withoutUI],
                              relativeTo: nil, bookmarkDataIsStale: &stale) {
            backgroundURL = url
            _ = url.startAccessingSecurityScopedResource()
            if stale { setBackground(url) }
        }
    }
}

struct QuoteItem {
    let english: String
    let source: String
    let translations: [AppLanguage: String]

    func localized(_ language: AppLanguage) -> String {
        translations[language] ?? english
    }

    static let all = [
        QuoteItem(
            english: "Our doubts are traitors, and make us lose the good we oft might win.",
            source: "Shakespeare · Measure for Measure",
            translations: [.zhHans: "我们的疑虑是叛徒，常使我们因畏惧尝试而失去本可赢得的美好。", .ja: "疑いは裏切り者。試すことを恐れ、手にできたはずの幸運を失わせる。", .es: "Nuestras dudas son traidoras y nos hacen perder el bien que a menudo podríamos ganar.", .fr: "Nos doutes sont des traîtres et nous font perdre le bien que nous pourrions souvent gagner.", .ar: "شكوكنا خائنة، فهي تجعلنا نفقد الخير الذي كان بوسعنا أن نناله.", .ko: "의심은 배신자라서, 시도했다면 얻었을 좋은 것을 잃게 한다."]
        ),
        QuoteItem(
            english: "Never give in—never, never, never, never.",
            source: "Winston Churchill",
            translations: [.zhHans: "永不屈服——永远、永远、永远、永远不要。", .ja: "決して屈するな。決して、決して、決して、決して。", .es: "Nunca cedas; nunca, nunca, nunca, nunca.", .fr: "Ne cédez jamais — jamais, jamais, jamais, jamais.", .ar: "لا تستسلم أبداً—أبداً، أبداً، أبداً، أبداً.", .ko: "절대 굴복하지 마라. 절대, 절대, 절대, 절대로."]
        ),
        QuoteItem(
            english: "When you have eliminated the impossible, whatever remains must be the truth.",
            source: "Sherlock Holmes · The Sign of Four",
            translations: [.zhHans: "排除一切不可能之后，剩下的无论多么不可思议，都必是真相。", .ja: "不可能なものをすべて除けば、残ったものがどれほど奇妙でも真実である。", .es: "Cuando has eliminado lo imposible, lo que queda debe ser la verdad.", .fr: "Lorsque vous avez éliminé l’impossible, ce qui reste doit être la vérité.", .ar: "حين تستبعد المستحيل، فلا بد أن يكون ما تبقّى هو الحقيقة.", .ko: "불가능한 것을 모두 제거하고 나면, 남은 것이 무엇이든 진실이다."]
        ),
        QuoteItem(
            english: "All for one, one for all.",
            source: "Alexandre Dumas · The Three Musketeers",
            translations: [.zhHans: "人人为我，我为人人。", .ja: "一人は皆のために、皆は一人のために。", .es: "Todos para uno y uno para todos.", .fr: "Tous pour un, un pour tous.", .ar: "الكل للواحد، والواحد للكل.", .ko: "모두는 하나를 위해, 하나는 모두를 위해."]
        ),
        QuoteItem(
            english: "Wait and hope.",
            source: "Alexandre Dumas · The Count of Monte Cristo",
            translations: [.zhHans: "等待，并心怀希望。", .ja: "待て、しかして希望せよ。", .es: "Esperar y confiar.", .fr: "Attendre et espérer.", .ar: "انتظر وكن على أمل.", .ko: "기다려라, 그리고 희망을 가져라."]
        )
    ]
}

struct RootView: View {
    @EnvironmentObject private var timer: FocusTimer
    @EnvironmentObject private var reminders: ReminderStore
    @EnvironmentObject private var language: LanguageManager
    @EnvironmentObject private var theme: ThemeManager
    @State private var section = 0
    @State private var showingAdd = false
    @State private var showingSettings = false
    @State private var quote = QuoteItem.all.randomElement()!

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(nsColor: .windowBackgroundColor), Color.primary.opacity(0.035), Color(hex: "D8D5CE").opacity(0.14)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ).ignoresSafeArea()
            if let url = theme.backgroundURL, let image = NSImage(contentsOf: url) {
                Image(nsImage: image).resizable().scaledToFill().opacity(theme.backgroundOpacity).ignoresSafeArea().clipped()
                Rectangle().fill(.ultraThinMaterial).ignoresSafeArea()
            }

            VStack(spacing: 14) {
                header
                Picker(L10n.text(.feature, language.selected), selection: $section) {
                    Text(L10n.text(.timer, language.selected)).tag(0)
                    Text(L10n.text(.reminders, language.selected)).tag(1)
                }
                .pickerStyle(.segmented).frame(width: 260)

                if section == 0 { TimerDashboard() } else { RemindersDashboard() }
            }
            .padding(24)
        }
        .sheet(isPresented: $showingAdd) { AddItemView(initialTab: section).frame(minWidth: 520) }
        .sheet(isPresented: $showingSettings) { SettingsView().frame(minWidth: 500) }
    }

    private var header: some View {
        HStack(alignment: .top, spacing: 16) {
            VStack(alignment: .leading, spacing: 9) {
                Button { showingAdd = true } label: {
                    Image(systemName: "plus").font(.title3.weight(.semibold)).frame(width: 22, height: 22)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .tint(Color(hex: "3C3D40"))
                .help(L10n.text(.newItem, language.selected))

                VStack(alignment: .leading, spacing: 4) {
                    Text("“\(quote.localized(language.selected))”")
                        .font(.callout.weight(.semibold))
                        .foregroundStyle(.primary)
                        .lineLimit(3)
                    if language.selected != .en {
                        Text("“\(quote.english)”")
                            .font(.caption)
                            .italic()
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                    }
                    Text(L10n.text(.quoteBy, language.selected, quote.source))
                        .font(.caption2.weight(.medium))
                        .foregroundStyle(Color(hex: "8C8E92"))
                }
                .frame(maxWidth: 390, alignment: .leading)
            }
            .onTapGesture { quote = QuoteItem.all.randomElement()! }
            Spacer(minLength: 12)
            HStack(spacing: 12) {
                Label("BellCat", systemImage: "sparkles")
                    .font(.title2.weight(.bold))
                    .foregroundStyle(.primary)
                Menu {
                    ForEach(AppLanguage.allCases) { option in
                        Button {
                            language.select(option)
                            reminders.refreshNotificationLanguage()
                        } label: { Text(option.nativeName + (option == language.selected ? " ✓" : "")) }
                    }
                } label: { Label(language.selected.nativeName, systemImage: "globe") }
                    .menuStyle(.borderlessButton).fixedSize()
                Button { showingSettings = true } label: { Image(systemName: "gearshape.fill") }
                    .buttonStyle(.borderless).font(.title3).foregroundStyle(.secondary)
                    .help(L10n.text(.settings, language.selected))
            }
        }
    }
}

struct TimerDashboard: View {
    @EnvironmentObject private var timer: FocusTimer
    @EnvironmentObject private var language: LanguageManager
    @EnvironmentObject private var ambience: AmbiencePlayer
    @State private var importingMusic = false

    var body: some View {
        VStack(spacing: 15) {
            Menu {
                ForEach(timer.routines) { routine in
                    Button { timer.selectRoutine(routine.id) } label: {
                        Text(routine.name + (routine.id == timer.selectedRoutineID ? " ✓" : ""))
                    }
                }
            } label: {
                Label(timer.currentRoutine.name, systemImage: "checklist")
                    .font(.headline).padding(.horizontal, 14).padding(.vertical, 7)
            }
            .menuStyle(.borderlessButton)

            InteractiveRoutineRing().frame(width: 340, height: 340)

            HStack(spacing: 14) {
                Button { timer.reset() } label: { Image(systemName: "arrow.counterclockwise") }
                    .buttonStyle(.bordered).controlSize(.large).help(L10n.text(.reset, language.selected))
                Button(action: timer.startPause) {
                    Label(timer.isRunning ? L10n.text(.pause, language.selected) : L10n.text(.start, language.selected),
                          systemImage: timer.isRunning ? "pause.fill" : "play.fill").frame(minWidth: 105)
                }
                .buttonStyle(.borderedProminent).controlSize(.large).tint(Color(hex: "3C3D40"))
            }

            HStack(spacing: 10) {
                Button(action: ambience.toggle) {
                    Image(systemName: ambience.isPlaying ? "pause.fill" : "play.fill")
                        .frame(width: 18)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "56585C"))
                .help(L10n.text(.whiteNoise, language.selected))

                Menu {
                    ForEach(AmbienceSound.allCases.filter { $0 != .custom || ambience.customURL != nil }) { sound in
                        Button { ambience.choose(sound) } label: {
                            Text(sound.title(language.selected) + (sound == ambience.selected ? " ✓" : ""))
                        }
                    }
                } label: {
                    Label(ambience.selected.title(language.selected), systemImage: "waveform")
                }
                .menuStyle(.borderlessButton)

                Button(L10n.text(.chooseMusic, language.selected)) { importingMusic = true }
                    .buttonStyle(.borderless)
            }
            .font(.subheadline)

            Text(L10n.text(.completedRounds, language.selected, timer.completedRounds))
                .font(.caption).foregroundStyle(.secondary)
        }
        .frame(maxHeight: .infinity)
        .fileImporter(isPresented: $importingMusic, allowedContentTypes: [.audio]) { result in
            if case .success(let url) = result { ambience.setCustomFile(url) }
        }
    }
}

struct InteractiveRoutineRing: View {
    @EnvironmentObject private var timer: FocusTimer
    @EnvironmentObject private var language: LanguageManager
    @State private var editingStageID: UUID?
    @State private var trail: [RingTrailPoint] = []
    @State private var isDraggingHandle = false

    private let colorPalette = ["34363A", "5B5E63", "8F939A", "C4C7CC", "8BA7B5", "A899B4"]

    var body: some View {
        GeometryReader { proxy in
            let size = min(proxy.size.width, proxy.size.height)
            let radius = size / 2 - 24
            ZStack {
                Circle().stroke(.primary.opacity(0.08), lineWidth: 24)
                ForEach(Array(timer.currentRoutine.stages.enumerated()), id: \.element.id) { index, stage in
                    let bounds = segmentBounds(index)
                    Circle()
                        .trim(from: min(bounds.0 + 0.004, bounds.1), to: max(bounds.0, bounds.1 - 0.004))
                        .stroke(Color(hex: stage.colorHex).opacity(index == timer.currentStageIndex ? 1 : 0.62),
                                style: StrokeStyle(lineWidth: index == timer.currentStageIndex ? 27 : 21, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                        .shadow(color: Color(hex: stage.colorHex).opacity(editingStageID == stage.id ? 0.52 : 0), radius: 8)
                        .onTapGesture {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.78)) {
                                timer.selectStage(index)
                                editingStageID = stage.id
                            }
                        }
                }

                trailLayer(radius: radius, size: proxy.size)

                Circle().fill(.white).shadow(color: .black.opacity(0.25), radius: 4)
                    .overlay(Circle().stroke(Color(hex: timer.currentStage.colorHex), lineWidth: 5))
                    .frame(width: 24, height: 24)
                    .padding(12)
                    .contentShape(Circle())
                    .offset(x: radius * cos(timer.sequenceProgress * 2 * .pi - .pi / 2),
                            y: radius * sin(timer.sequenceProgress * 2 * .pi - .pi / 2))
                    .scaleEffect(isDraggingHandle ? 1.2 : 1)
                    .shadow(color: Color(hex: timer.currentStage.colorHex).opacity(isDraggingHandle ? 0.8 : 0.3),
                            radius: isDraggingHandle ? 12 : 4)
                    .gesture(handleDragGesture(in: proxy.size))

                VStack(spacing: 7) {
                    Text(timer.currentStage.title(language.selected)).font(.headline)
                        .foregroundStyle(Color(hex: timer.currentStage.colorHex))
                    Text(timer.remainingText).font(.system(size: 58, weight: .medium, design: .rounded)).monospacedDigit()
                    Text(L10n.text(.clickDragHint, language.selected)).font(.caption).foregroundStyle(.secondary)
                    if let stage = editingStage {
                        stageColorEditor(stage)
                            .transition(.scale(scale: 0.92).combined(with: .opacity))
                    }
                }
            }
            .coordinateSpace(name: "BellCatRing")
            .onChange(of: timer.selectedRoutineID) { _ in editingStageID = nil }
        }
    }

    private var editingStage: TaskStage? {
        guard let id = editingStageID else { return nil }
        return timer.currentRoutine.stages.first(where: { $0.id == id })
    }

    private func stageColorEditor(_ stage: TaskStage) -> some View {
        HStack(spacing: 7) {
            Text(L10n.text(.stageColor, language.selected))
                .font(.caption.weight(.semibold)).foregroundStyle(.secondary)
            ForEach(colorPalette, id: \.self) { hex in
                Button { timer.updateStageColor(stage.id, hex: hex) } label: {
                    Circle().fill(Color(hex: hex))
                        .overlay(Circle().stroke(.primary.opacity(stage.colorHex.uppercased() == hex ? 0.8 : 0.14), lineWidth: 1.5))
                        .frame(width: 16, height: 16)
                }
                .buttonStyle(.plain)
            }
            ColorPicker("", selection: colorBinding(for: stage), supportsOpacity: false)
                .labelsHidden().frame(width: 24)
                .help(L10n.text(.customColor, language.selected))
            Button { withAnimation { editingStageID = nil } } label: {
                Image(systemName: "xmark.circle.fill").foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 11).padding(.vertical, 7)
        .background(.ultraThinMaterial, in: Capsule())
    }

    private func colorBinding(for stage: TaskStage) -> Binding<Color> {
        Binding(
            get: { Color(hex: stage.colorHex) },
            set: { timer.updateStageColor(stage.id, hex: $0.hexString) }
        )
    }

    private func handleDragGesture(in size: CGSize) -> some Gesture {
        DragGesture(minimumDistance: 0, coordinateSpace: .named("BellCatRing"))
            .onChanged { value in
                isDraggingHandle = true
                let fraction = ringFraction(at: value.location, in: size)
                timer.seek(to: fraction)
                let now = Date()
                if trail.last.map({ now.timeIntervalSince($0.createdAt) > 0.018 || abs($0.fraction - fraction) > 0.004 }) ?? true {
                    trail.append(RingTrailPoint(fraction: fraction, createdAt: now))
                    if trail.count > 24 { trail.removeFirst(trail.count - 24) }
                }
            }
            .onEnded { value in
                timer.seek(to: ringFraction(at: value.location, in: size))
                withAnimation(.spring(response: 0.24, dampingFraction: 0.62)) { isDraggingHandle = false }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.72) {
                    if !isDraggingHandle { trail.removeAll() }
                }
            }
    }

    private func trailLayer(radius: CGFloat, size: CGSize) -> some View {
        TimelineView(.animation(minimumInterval: 1.0 / 60.0, paused: trail.isEmpty)) { timeline in
            Canvas { context, _ in
                let now = timeline.date
                for (index, point) in trail.enumerated() {
                    let age = now.timeIntervalSince(point.createdAt)
                    guard age < 0.72 else { continue }
                    let life = max(0, 1 - age / 0.72)
                    let rank = Double(index + 1) / Double(max(1, trail.count))
                    let diameter = CGFloat(4 + 12 * life * rank)
                    let theta = point.fraction * 2 * .pi - .pi / 2
                    let center = CGPoint(x: size.width / 2 + radius * cos(theta),
                                         y: size.height / 2 + radius * sin(theta))
                    let rect = CGRect(x: center.x - diameter / 2, y: center.y - diameter / 2,
                                      width: diameter, height: diameter)
                    context.fill(Path(ellipseIn: rect),
                                 with: .color(Color(hex: timer.currentStage.colorHex).opacity(0.56 * life * rank)))
                }
            }
        }
        .allowsHitTesting(false)
    }

    private func ringFraction(at point: CGPoint, in size: CGSize) -> Double {
        let dx = point.x - size.width / 2
        let dy = point.y - size.height / 2
        var angle = atan2(dy, dx) + .pi / 2
        if angle < 0 { angle += 2 * .pi }
        return angle / (2 * .pi)
    }

    private func segmentBounds(_ index: Int) -> (Double, Double) {
        let stages = timer.currentRoutine.stages
        let total = Double(max(1, stages.reduce(0) { $0 + $1.minutes }))
        let start = Double(stages.prefix(index).reduce(0) { $0 + $1.minutes }) / total
        let end = start + Double(stages[index].minutes) / total
        return (start, end)
    }
}

private struct RingTrailPoint {
    let fraction: Double
    let createdAt: Date
}

struct RemindersDashboard: View {
    @EnvironmentObject private var store: ReminderStore
    @EnvironmentObject private var language: LanguageManager

    var body: some View {
        Group {
            if store.items.isEmpty {
                VStack(spacing: 12) {
                    Spacer()
                    Image(systemName: "bell.and.waves.left.and.right.fill").font(.system(size: 44)).foregroundStyle(Color(hex: "66686C"))
                    Text(L10n.text(.noReminders, language.selected)).font(.headline)
                    Text(L10n.text(.reminderExample, language.selected)).foregroundStyle(.secondary)
                    Spacer()
                }
            } else {
                List {
                    ForEach(store.items) { item in
                        HStack(spacing: 14) {
                            Image(systemName: item.style == .alarm ? "alarm.fill" : "bell.fill")
                                .font(.title2).foregroundStyle(Color(hex: "66686C"))
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.title).font(.headline)
                                Text(L10n.date(item.eventDate, language.selected))
                                Text(item.advanceText(language: language.selected)).font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer()
                            if item.fireDate < Date() { Text(L10n.text(.expired, language.selected)).foregroundStyle(.secondary) }
                            else {
                                Toggle("", isOn: Binding(get: { item.isEnabled }, set: { store.setEnabled($0, for: item) }))
                                    .labelsHidden()
                            }
                        }.padding(.vertical, 6)
                    }.onDelete(perform: store.delete)
                }.scrollContentBackground(.hidden)
            }
        }.frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct AddItemView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var language: LanguageManager
    @State var initialTab: Int

    var body: some View {
        VStack(spacing: 18) {
            Picker(L10n.text(.newItem, language.selected), selection: $initialTab) {
                Text(L10n.text(.routine, language.selected)).tag(0)
                Text(L10n.text(.reminders, language.selected)).tag(1)
            }.pickerStyle(.segmented)
            if initialTab == 0 { NewTaskView() } else { NewReminderView() }
        }.padding(26)
    }
}

struct StageDraft: Identifiable {
    let id = UUID()
    var kind: StageKind
    var name: String
    var minutes: Int
    var colorHex: String
}

struct NewTaskView: View {
    @EnvironmentObject private var timer: FocusTimer
    @EnvironmentObject private var language: LanguageManager
    @Environment(\.dismiss) private var dismiss
    @State private var name = ""
    @State private var stages = [
        StageDraft(kind: .work, name: "", minutes: 25, colorHex: "4B4D51"),
        StageDraft(kind: .rest, name: "", minutes: 5, colorHex: "A7A9AD")
    ]
    private let palette = ["4B4D51", "A7A9AD", "D1CEC6", "6E7074", "B9BBC0", "34363A"]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(L10n.text(.createTask, language.selected)).font(.title2.bold())
            TextField(L10n.text(.taskName, language.selected), text: $name)
            ForEach($stages) { $stage in
                HStack {
                    Circle().fill(Color(hex: stage.colorHex)).frame(width: 14, height: 14)
                    Picker("", selection: $stage.kind) {
                        ForEach(StageKind.allCases) { Text($0.title(language.selected)).tag($0) }
                    }.labelsHidden().frame(width: 105)
                    if stage.kind == .other {
                        TextField(L10n.text(.stageName, language.selected), text: $stage.name)
                    }
                    Stepper(L10n.text(.taskDuration, language.selected, stage.minutes), value: $stage.minutes, in: 1...180)
                    if stages.count > 1 {
                        Button { stages.removeAll { $0.id == stage.id } } label: { Image(systemName: "minus.circle") }
                            .buttonStyle(.borderless)
                    }
                }
            }
            Button { stages.append(StageDraft(kind: .other, name: "", minutes: 10, colorHex: palette[stages.count % palette.count])) } label: {
                Label(L10n.text(.addStage, language.selected), systemImage: "plus.circle")
            }
            HStack {
                Spacer()
                Button(L10n.text(.cancel, language.selected)) { dismiss() }
                Button(L10n.text(.createTask, language.selected)) {
                    let routine = FocusRoutine(
                        name: name.isEmpty ? L10n.text(.focusWork, language.selected) : name,
                        stages: stages.enumerated().map { index, draft in
                            TaskStage(kind: draft.kind, customName: draft.name, minutes: draft.minutes,
                                      colorHex: draft.colorHex.isEmpty ? palette[index % palette.count] : draft.colorHex)
                        }
                    )
                    timer.addRoutine(routine); dismiss()
                }.buttonStyle(.borderedProminent).tint(Color(hex: "3C3D40"))
            }
        }
    }
}

struct NewReminderView: View {
    enum Unit: Int, CaseIterable, Identifiable { case minutes = 1, hours = 60, days = 1440; var id: Self { self } }
    @EnvironmentObject private var store: ReminderStore
    @EnvironmentObject private var language: LanguageManager
    @Environment(\.dismiss) private var dismiss
    @State private var title = L10n.text(.airportDefault)
    @State private var eventDate = Calendar.current.date(byAdding: .day, value: 1, to: Date()) ?? Date()
    @State private var advanceValue = 3
    @State private var unit: Unit = .hours
    @State private var style: ReminderItem.AlertStyle = .notification

    private var fireDate: Date { eventDate.addingTimeInterval(TimeInterval(-advanceValue * unit.rawValue * 60)) }
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(L10n.text(.newReminder, language.selected)).font(.title2.bold())
            TextField(L10n.text(.reminderName, language.selected), text: $title)
            DatePicker(L10n.text(.eventDateTime, language.selected), selection: $eventDate)
            HStack {
                Text(L10n.text(.advance, language.selected))
                TextField("3", value: $advanceValue, format: .number).frame(width: 60)
                Picker("", selection: $unit) {
                    Text(L10n.text(.minutes, language.selected)).tag(Unit.minutes)
                    Text(L10n.text(.hours, language.selected)).tag(Unit.hours)
                    Text(L10n.text(.days, language.selected)).tag(Unit.days)
                }.labelsHidden().frame(width: 100)
            }
            Picker(L10n.text(.alertMethod, language.selected), selection: $style) {
                Text(L10n.text(.notification, language.selected)).tag(ReminderItem.AlertStyle.notification)
                Text(L10n.text(.alarm, language.selected)).tag(ReminderItem.AlertStyle.alarm)
            }.pickerStyle(.segmented)
            Text(L10n.text(.willRemind, language.selected, L10n.date(fireDate, language.selected)))
                .font(.callout).foregroundStyle(fireDate > Date() ? Color.secondary : Color.red)
            HStack {
                Spacer()
                Button(L10n.text(.cancel, language.selected)) { dismiss() }
                Button(L10n.text(.saveReminder, language.selected)) {
                    store.add(ReminderItem(title: title, eventDate: eventDate,
                                           advanceMinutes: advanceValue * unit.rawValue, style: style))
                    dismiss()
                }.buttonStyle(.borderedProminent).tint(Color(hex: "3C3D40")).disabled(title.isEmpty || fireDate <= Date())
            }
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject private var timer: FocusTimer
    @EnvironmentObject private var theme: ThemeManager
    @EnvironmentObject private var language: LanguageManager
    @Environment(\.dismiss) private var dismiss
    @State private var importingSound = false
    @State private var importingBackground = false

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text(L10n.text(.settings, language.selected)).font(.title2.bold())
            Text(L10n.text(.theme, language.selected)).font(.headline)
            Picker(L10n.text(.appearance, language.selected), selection: Binding(
                get: { theme.appearance }, set: { theme.setAppearance($0) }
            )) {
                Text(L10n.text(.systemMode, language.selected)).tag(ThemeManager.Appearance.system)
                Text(L10n.text(.lightMode, language.selected)).tag(ThemeManager.Appearance.light)
                Text(L10n.text(.darkMode, language.selected)).tag(ThemeManager.Appearance.dark)
            }.pickerStyle(.segmented)

            Text(L10n.text(.backgroundImage, language.selected)).font(.headline)
            HStack {
                Button(L10n.text(.chooseBackground, language.selected)) { importingBackground = true }
                if theme.backgroundURL != nil { Button(L10n.text(.removeBackground, language.selected)) { theme.removeBackground() } }
            }
            HStack {
                Text(L10n.text(.backgroundOpacity, language.selected, Int(theme.backgroundOpacity * 100)))
                Slider(value: Binding(get: { theme.backgroundOpacity }, set: { theme.setOpacity($0) }), in: 0...1)
            }

            Divider()
            Text(L10n.text(.endSound, language.selected)).font(.headline)
            HStack {
                Picker(L10n.text(.sound, language.selected), selection: $timer.soundChoice) {
                    Text("Glass").tag("Glass"); Text("Ping").tag("Ping"); Text("Funk").tag("Funk")
                    if let url = timer.customSoundURL { Text(L10n.text(.customFile, language.selected, url.lastPathComponent)).tag("custom") }
                }
                .pickerStyle(.menu)
                .onChange(of: timer.soundChoice) { _ in timer.stopSoundPreview() }
                Spacer()
                Button(action: timer.toggleSoundPreview) {
                    Label(
                        L10n.text(timer.isPreviewingSound ? .stopPreview : .previewSixSeconds, language.selected),
                        systemImage: timer.isPreviewingSound ? "stop.fill" : "play.fill"
                    )
                }
                .buttonStyle(.bordered)
                .tint(Color(hex: "56585C"))
            }
            HStack {
                Button(L10n.text(.chooseAudio, language.selected)) { importingSound = true }
                Spacer()
                Button(L10n.text(.done, language.selected)) { dismiss() }.buttonStyle(.borderedProminent).tint(Color(hex: "3C3D40"))
            }
        }
        .padding(28)
        .fileImporter(isPresented: $importingBackground, allowedContentTypes: [.image]) { result in
            if case .success(let url) = result { theme.setBackground(url) }
        }
        .fileImporter(isPresented: $importingSound, allowedContentTypes: [.audio]) { result in
            if case .success(let url) = result {
                timer.stopSoundPreview(); timer.customSoundURL = url; timer.soundChoice = "custom"
            }
        }
        .onDisappear { timer.stopSoundPreview() }
    }
}

extension Color {
    init(hex: String) {
        let clean = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var value: UInt64 = 0
        Scanner(string: clean).scanHexInt64(&value)
        let r = Double((value >> 16) & 0xff) / 255
        let g = Double((value >> 8) & 0xff) / 255
        let b = Double(value & 0xff) / 255
        self.init(red: r, green: g, blue: b)
    }

    var hexString: String {
        guard let color = NSColor(self).usingColorSpace(.deviceRGB) else { return "4B4D51" }
        return String(format: "%02X%02X%02X", Int(color.redComponent * 255),
                      Int(color.greenComponent * 255), Int(color.blueComponent * 255))
    }
}
