//USEUNIT start_notepad

function Print()
{
    LaunchNotePad();
    Sys.Keys("~F");
    Sys.Keys("P");
    Aliases.dlg_Print.btn_Cancel.ClickButton();
    CloseNotePad();
}