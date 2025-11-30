[Setup]
AppName=ProfitLift
AppVersion=1.0.0
AppPublisher=ProfitLift Team
DefaultDirName={pf}\ProfitLift
DefaultGroupName=ProfitLift
OutputDir=Output
OutputBaseFilename=ProfitLift-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\ProfitLift.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config\*.yaml"; DestDir: "{app}\config"; Flags: ignoreversion
Source: "data\sample\*.csv"; DestDir: "{app}\data\sample"; Flags: ignoreversion

[Icons]
Name: "{group}\ProfitLift"; Filename: "{app}\ProfitLift.exe"
Name: "{group}\Uninstall ProfitLift"; Filename: "{uninstallexe}"
Name: "{commondesktop}\ProfitLift"; Filename: "{app}\ProfitLift.exe"

[Run]
Filename: "{app}\ProfitLift.exe"; Description: "Launch ProfitLift"; Flags: nowait postinstall skipifsilent
