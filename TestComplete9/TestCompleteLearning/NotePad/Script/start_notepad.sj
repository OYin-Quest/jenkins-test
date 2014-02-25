function LaunchNotePad()
{
    var shellObj = Sys.OleObject("WScript.Shell");
    shellObj.Run("%windir%\\system32\\notepad.exe");
    Aliases.wnd_Notepad.Activate();
}

function CloseNotePad()
{
    Aliases.wnd_Notepad.Activate();
    Aliases.wnd_Notepad.Close();
}