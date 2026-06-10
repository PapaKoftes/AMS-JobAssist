; ============================================================================
;  AMS JobAssist - Inno Setup installer script
;
;  Produces: AMS-JobAssist-Setup.exe
;
;  Prerequisites:
;    1. Run build_all.bat first to produce the 3 .exe files in dist\
;    2. Install Inno Setup 6+ from https://jrsoftware.org/isinfo.php
;    3. Compile: iscc packaging\installer.iss
;       (or open in Inno Setup and press Compile)
;
;  The installer:
;    - Copies the 3 .exe files to {autopf}\AMS JobAssist
;    - Creates Start Menu entries (Launcher + Uninstall)
;    - Creates a Desktop shortcut (optional)
;    - Creates a data directory at {userappdata}\AMS-JobAssist
;    - Registers in Add/Remove Programs with proper uninstall
;    - Uninstall preserves data by default, offers to remove it
; ============================================================================

#define MyAppName      "AMS JobAssist"
#define MyAppVersion   "1.0"
#define MyAppPublisher "Mina Mikail"
#define MyAppURL       "https://github.com/PapaKoftes/AMS-JobAssist"
#define MyAppExeName   "AMS-JobAssist-Launcher.exe"

[Setup]
AppId={{B7A3F2D1-4E5C-4A8B-9D6F-1C2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output to packaging\output\
OutputDir=output
OutputBaseFilename=AMS-JobAssist-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Require 64-bit Windows
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; No admin rights needed — install to user's Program Files
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Minimum Windows 10
MinVersion=10.0
; German as default language
ShowLanguageDialog=auto

[Languages]
Name: "german";  MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
german.BeveledLabel=AMS JobAssist - Lebenslauf-Assistent fuer AMS-Kurse
english.BeveledLabel=AMS JobAssist - CV Assistant for AMS Courses

[CustomMessages]
german.LaunchAfterInstall=AMS JobAssist jetzt starten
english.LaunchAfterInstall=Launch AMS JobAssist now
german.CreateDesktopIcon=Desktop-Verknuepfung erstellen
english.CreateDesktopIcon=Create desktop shortcut
german.DataDirInfo=Daten werden gespeichert in: %1
english.DataDirInfo=Data will be stored in: %1
german.DeleteDataPrompt=Moechten Sie auch alle gespeicherten Lebenslaeufe und Daten loeschen?%nDieser Schritt kann NICHT rueckgaengig gemacht werden.
english.DeleteDataPrompt=Do you also want to delete all saved CVs and data?%nThis action CANNOT be undone.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executables from dist\
Source: "..\dist\AMS-JobAssist-Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\AMS-JobAssist-Tool1.exe";    DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\AMS-JobAssist-Tool2.exe";    DestDir: "{app}"; Flags: ignoreversion
; Icon
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; Bundled AI model — must sit beside the .exe at {app}\data\models, where the
; frozen app looks for it (local_llm.py _MODEL_DIR frozen branch). Without this
; the app silently drops to rules-only. 'external'+'skipifsourcedoesntexist' so
; the build still produces an installer if the model wasn't pre-seeded.
Source: "..\dist\data\models\*.gguf"; DestDir: "{app}\data\models"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; Create a data directory with user-writable permissions
Name: "{userappdata}\AMS-JobAssist"
Name: "{userappdata}\AMS-JobAssist\data"
Name: "{userappdata}\AMS-JobAssist\models"
Name: "{userappdata}\AMS-JobAssist\exports"
Name: "{userappdata}\AMS-JobAssist\backups"

[Icons]
; Start Menu
Name: "{group}\AMS JobAssist";            Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Comment: "Lebenslauf-Assistent starten"
Name: "{group}\AMS JobAssist deinstallieren"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
; Desktop (optional)
Name: "{autodesktop}\AMS JobAssist";      Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
; Launch after install (optional checkbox on last page)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchAfterInstall}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Nothing special — just let Inno handle it

[UninstallDelete]
; Clean up any runtime temp files the .exe may have created
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.log"

[Code]
// Ask whether to delete user data on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\AMS-JobAssist');
    if DirExists(DataDir) then
    begin
      if MsgBox(CustomMessage('DeleteDataPrompt'), mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;

// Show data directory path during install
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;
