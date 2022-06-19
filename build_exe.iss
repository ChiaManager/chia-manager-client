; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define Name "Chia Manager Client"
#define Version "1.0"
#define Publisher "ChiaManager"
#define PublisherURL "chia-manager.org"
#define ExeName "ChiaManagerClient.exe"

[Setup]
AppId={{567357E3-4A51-430E-8428-271A4763A737}
AppName={#Name}
AppVersion={#Version}
AppVerName={#Name} {#Version}
AppPublisher={#Publisher}
AppPublisherURL={#PublisherURL}
AppSupportURL={#PublisherURL}
AppUpdatesURL={#PublisherURL}
DefaultDirName={userpf}\{#Name}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputDir=output
OutputBaseFilename=ChiaManagerClient
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "ChiaManagerClient.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "config\example.node.ini"; DestDir: "{app}\config\"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#Name}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#Name}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ExeName}"; Description: "{cm:LaunchProgram,{#StringChange(Name, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runhidden;

