//USEUNIT start_notepad

function TestMethod()
{
    LaunchNotePad();
    Log.Message(Aliases.wnd_Notepad.WndCaption);
}