//USEUNIT Lib

function Csv_Reader(name, value)
{
  var driver = DDT.CSVDriver(Files.FileNameByName("TICAdminConsoleZhu_csv"));
  var dicArrObj = new Array();
  var index = 0;
  try
  {
    while (!driver.EOF())
    {
      var dicObj = new ActiveXObject("Scripting.Dictionary");
      var valid = false;
      for (var i = 0; i < driver.ColumnCount; i ++)
      {
        var colName = driver.ColumnName(i);
        var colValue = driver.Value(i);
        if (colName == name && colValue == value)
        {
          valid = true;
        }
        //Log.Message(driver.ColumnName(i) + " : " + aqConvert.VarToStr(driver.Value(i)));
        dicObj.Add(colName, colValue);
      }
      if (valid)
      {
        dicArrObj[index++] = dicObj;
      }
      driver.Next();
    }
  }
  catch(e)
  {
  
  }
  finally
  {
    DDT.CloseDriver(driver.Name);
    return dicArrObj;
  }
}

function TST()
{
  var t = Csv_Reader("ArtifactType", "Automation Scripts");
  
  for (var i = 0; i < t.length; i ++)
  {
    Lib.DumpDictionary(t[i]);
  }
}