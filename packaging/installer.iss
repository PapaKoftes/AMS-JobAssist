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
;    - Downloads + SHA-256-verifies the ~1.9 GB AI model during setup (optional
;      task, ticked by default) so the installer itself stays small (~250 MB)
;    - Creates Start Menu entries (Launcher + Uninstall)
;    - Creates a Desktop shortcut (optional)
;    - Creates a data directory at {userappdata}\AMS-JobAssist
;    - Registers in Add/Remove Programs with proper uninstall
;    - Uninstall preserves data by default, offers to remove it
; ============================================================================

#define MyAppName      "AMS JobAssist"
#define MyAppVersion   "1.0.0"
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
; The bundled GGUF model (~1.9 GB) is already quantized/incompressible, so heavy
; LZMA (ultra64) costs many minutes of build time for ~0 size gain. 'normal' keeps
; the exes well-compressed without the pointless churn on the model.
Compression=lzma2/normal
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
german.DownloadModelGroup=KI-Modell (lokale Offline-KI):
english.DownloadModelGroup=AI model (local offline AI):
german.DownloadModelTask=KI-Modell jetzt herunterladen (~1,9 GB, Internetverbindung erforderlich)
english.DownloadModelTask=Download the AI model now (~1.9 GB, internet connection required)
german.DownloadModelTitle=KI-Modell wird heruntergeladen
english.DownloadModelTitle=Downloading the AI model
german.DownloadModelDesc=Das Offline-KI-Modell (~1,9 GB) wird einmalig von HuggingFace geladen und per SHA-256 geprueft. Danach laeuft die App vollstaendig offline.
english.DownloadModelDesc=The offline AI model (~1.9 GB) is fetched once from HuggingFace and verified by SHA-256. After that the app runs fully offline.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
; Download the ~1.9 GB AI model during setup (ticked by default; untick to run
; rule-based only and fetch the model later). Keeps the installer itself small.
Name: "downloadmodel"; Description: "{cm:DownloadModelTask}"; GroupDescription: "{cm:DownloadModelGroup}"

[Files]
; Main executables from dist\
Source: "..\dist\AMS-JobAssist-Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\AMS-JobAssist-Tool1.exe";    DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\AMS-JobAssist-Tool2.exe";    DestDir: "{app}"; Flags: ignoreversion
; Icon
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; AI model — NOT bundled, so the installer stays small (~250 MB, GitHub-friendly).
; It is downloaded from HuggingFace during setup (see [Code]) into {tmp}, verified
; by SHA-256, then placed beside the .exe at {app}\data\models where the frozen app
; looks for it (local_llm.py _MODEL_DIR frozen branch). 'external' = the source is
; the file fetched to {tmp}; 'skipifsourcedoesntexist' so the install still
; completes (rule-based only) if the user unticked the download task.
Source: "{tmp}\qwen2.5-3b-instruct-q4_k_m.gguf"; DestDir: "{app}\data\models"; Flags: external ignoreversion skipifsourcedoesntexist

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
var
  DownloadPage: TDownloadWizardPage;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(CustomMessage('DownloadModelTitle'), CustomMessage('DownloadModelDesc'), nil);
end;

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

// Download (and SHA-256-verify) the AI model during setup, unless the user
// unticked the "download model" task. On the Ready page we fetch it to {tmp};
// the [Files] 'external' entry then installs it into {app}\data\models.
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if (CurPageID = wpReady) and WizardIsTaskSelected('downloadmodel') then
  begin
    DownloadPage.Clear;
    // Pinned to the GitHub Release asset (immutable) rather than HuggingFace's
    // mutable /resolve/main/ URL — HF re-quantizes in place, which breaks the
    // SHA-256 verification. This file's hash matches the pin below exactly.
    DownloadPage.Add(
      'https://github.com/PapaKoftes/AMS-JobAssist/releases/download/v1.0.0/qwen2.5-3b-instruct-q4_k_m.gguf',
      'qwen2.5-3b-instruct-q4_k_m.gguf',
      '5ee4f07cdb9beadbbb293e85803c569b01bd37ed059d2715faa7bb405f31caa6');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        Result := True;
      except
        if not DownloadPage.AbortedByUser then
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end
  else
    Result := True;
end;
