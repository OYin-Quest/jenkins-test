//USEUNIT start_notepad

function Print()
{
    LaunchNotePad();
    Sys.Keys("~F");
    Sys.Keys("P");
    Aliases.dlg_Print.btn_Cancel.ClickButton();
    CloseNotePad();
}

function PrintSetup()
{
    LaunchNotePad();
    Sys.Keys("~F");
    Sys.Keys("u");
    Aliases.dlg_PageSetup.btn_Cancel.ClickButton();
}
