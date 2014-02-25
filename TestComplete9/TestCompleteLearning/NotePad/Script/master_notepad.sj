//USEUNIT start_notepad

function TestMethod()
{
    Log.Message("TestMethod");
    LaunchNotePad();
    Log.Message(Aliases.wnd_Notepad.WndCaption + "abc");
}