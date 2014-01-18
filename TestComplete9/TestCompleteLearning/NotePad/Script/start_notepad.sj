function LaunchNotePad()
{
    var shellObj = Sys.OleObject("WScript.Shell");
    shellObj.Run("%windir%\\system32\\notepad.exe");
}