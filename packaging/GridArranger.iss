; Grid Arranger for LightBurn — instalátor pro Windows (Inno Setup 6.3+), spec. v1.11 kap. 31.2, ADR-0004.
; Nespouštět ručně — sestavuje tools\build_exe.py, které předá:
;   /DAppVersion=0.1.0-alpha.2  /DVersionNumeric=0.1.0.0  /DSourceDir=...\dist\GridArranger  /DOutputDir=...\dist
;
; * Instalace jen pro aktuálního uživatele, bez práv správce ({autopf} = %LOCALAPPDATA%\Programs).
; * Nová verze se instaluje přes starou (stejné AppId); složka _internal se předem smaže,
;   aby v ní nezůstaly soubory staré verze. Nastavení uživatele (registr HKCU) zůstává.
; * Aktualizace z aplikace spouští instalátor s /SILENT; po dokončení se aplikace znovu spustí.

#ifndef AppVersion
  #error AppVersion is not defined - build with tools\build_exe.py
#endif
#ifndef VersionNumeric
  #define VersionNumeric "0.0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\dist\GridArranger"
#endif
#ifndef OutputDir
  #define OutputDir "..\dist"
#endif

#define AppName "Grid Arranger for LightBurn"
#define AppExe "GridArranger.exe"
#define RepoUrl "https://github.com/Knapis522/lightburn-grid-arranger"

[Setup]
; AppId se nesmí nikdy změnit — podle něj instalátor pozná předchozí instalaci.
AppId={{8C6E2F3A-5B1D-4E7A-9C2F-3D8B6A1E4F70}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Knapis522
AppPublisherURL={#RepoUrl}
AppUpdatesURL={#RepoUrl}/releases
VersionInfoVersion={#VersionNumeric}
VersionInfoProductVersion={#VersionNumeric}
VersionInfoDescription={#AppName} Setup
DefaultDirName={autopf}\Grid Arranger
DefaultGroupName=Grid Arranger
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir={#OutputDir}
OutputBaseFilename=GridArranger-Setup-v{#AppVersion}-win-x64
SetupIconFile=GridArranger.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
ShowLanguageDialog=auto

[Languages]
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
; běžná instalace: zaškrtávátko „Spustit“ na konci průvodce
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
; aktualizace z aplikace (/SILENT): po instalaci aplikaci znovu spustit
Filename: "{app}\{#AppExe}"; Flags: nowait; Check: WizardSilent
