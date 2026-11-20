Set s=CreateObject("WScript.Shell")
s.CurrentDirectory=CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
s.Run "cmd /c run_keno.bat",0,False
