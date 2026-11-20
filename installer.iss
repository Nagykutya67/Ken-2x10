[Setup]
AppName=Keno 2x10 Analytics
AppVersion=2.1.0
DefaultDirName={autopf}\Keno2x10
DefaultGroupName=Keno 2x10
OutputBaseFilename=Keno2x10_Setup_v2.1.0
Compression=lzma2
SolidCompression=yes
[Files]
Source: "dist\Keno2x10-v2.1\*"; DestDir: "{app}"; Flags: recursesubdirs
[Icons]
Name: "{group}\Keno 2x10"; Filename: "{app}\Keno2x10-v2.1.exe"
Name: "{autodesktop}\Keno 2x10"; Filename: "{app}\Keno2x10-v2.1.exe"
