#define MyAppName "BellCat"
#define MyAppVersion "2.1.1"
#define MyAppPublisher "BellCat contributors"
#define MyAppExeName "BellCat.exe"

[Setup]
AppId={{9B9BC278-7C5D-4D9E-922E-F021C53E5317}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=BellCat-2.1.1-Windows-x64-Setup
SetupIconFile=AppResources\BellCat.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\BellCat.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "CrossPlatform\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BellCat"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall BellCat"; Filename: "{uninstallexe}"
Name: "{autodesktop}\BellCat"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch BellCat"; Flags: nowait postinstall skipifsilent
