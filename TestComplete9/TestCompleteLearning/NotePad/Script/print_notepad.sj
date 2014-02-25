//USEUNIT start_notepad

function PrintSetup()
{
    LaunchNotePad();
    Sys.Keys("~F");
    Sys.Keys("u");
    Aliases.dlg_PageSetup.btn_Cancel.ClickButton();
}