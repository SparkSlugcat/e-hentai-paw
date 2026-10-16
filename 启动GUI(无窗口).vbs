Option Explicit
' ============================================================
'  e-hentai-paw 无窗口启动器 —— 双击本文件打开图形界面
'
'  为什么需要它：双击 .bat 时，那一下必须由 cmd.exe 去解析，
'  命令行窗口一定会出现（哪怕里面立刻 start 了 pythonw，也会闪）。
'  想让窗口彻底不出现，入口就不能是 .bat —— 本文件由 wscript.exe
'  执行，而 wscript 是 GUI 子系统程序，自己不带控制台。
'
'  做法：先以「隐藏窗口」跑同目录的 启动GUI.bat silent；
'        它返回非 0（说明启动自检没过）就再用「可见窗口」跑一次
'        启动GUI.bat，把报错和 pause 摆到眼前。
' ============================================================

Dim fso, sh, here, bat, rc
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

here = fso.GetParentFolderName(WScript.ScriptFullName)
bat  = here & "\启动GUI.bat"

If Not fso.FileExists(bat) Then
    MsgBox "找不到 启动GUI.bat ——它得和本文件放在同一个目录：" & vbCrLf & bat, 16, "e-hentai-paw"
    WScript.Quit 1
End If

' Run(命令, 窗口样式, 是否等它结束)：0 = 隐藏窗口，True = 等它跑完。
' 路径带空格和中文，整条命令两头各加双引号（VBS 里双引号写成四个 """"）。
rc = sh.Run("""" & bat & """" & " silent", 0, True)

If rc <> 0 Then
    ' 1 = 正常显示窗口。这次不传 silent，所以 启动GUI.bat 会 pause，
    ' 用户能看到失败的真正原因，而不是"双击了没反应"。
    sh.Run """" & bat & """", 1, True
End If
