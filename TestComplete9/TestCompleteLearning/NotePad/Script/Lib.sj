
function GetDataFromXml()
{
  var t = XML.User.Document.documentElement;
  
  //ProcessNodeOne(t);
  
  //return;
  var users = t.selectNodes("//user");
  
  var results = new Array();
  
  for (var i = 0; i < users.length; i ++)
  {
    results.push(ProcessNodeB(users.item(i)));
  }
  
  
  DumpObject(results, "User");
  //var obj = {};
  
  //var o = ProcessNode(users, obj);
  
  Log.Message("end");
}

function ProcessNodeB(xmlNode)
{
  var obj = {};
  var childNodes = xmlNode.childNodes;
  if (childNodes.length == 0)
  {
    return null;
  }
  else if (childNodes.length == 1 && aqObject.GetVarType(xmlNode.firstChild.nodeValue) != 1)
  {
    return xmlNode.firstChild.nodeValue;
  }
  else if (childNodes.length > 0)
  {
    //obj[xmlNode.nodeName] = {};
    for( var i = 0; i < childNodes.length; i ++)
    {
      var childNodeName = childNodes.item(i).nodeName;
      if (xmlNode.selectNodes("./" + childNodeName).length > 1)
      {
        if (obj[childNodeName] == undefined)
        {
          obj[childNodeName] = new Array();
        }
        obj[childNodeName].push(ProcessNodeB(childNodes.item(i)));
      }
      else
      {
        obj[childNodeName] = ProcessNodeB(childNodes.item(i));
      }
    }
  }
  return obj;
}

function ProcessNode(xmlNode, obj)
{
  var childNodes = xmlNode.childNodes;
  if (childNodes.length == 0)
  {
    obj[xmlNode.nodeName] = null;
  }
  else if (childNodes.length == 1 && aqObject.GetVarType(xmlNode.firstChild.nodeValue) != 1)
  {
    obj[xmlNode.nodeName] = xmlNode.firstChild.nodeValue;
  }
  else if (childNodes.length > 0)
  {
    obj[xmlNode.nodeName] = {};
  
    for( var i = 0; i < childNodes.length; i ++)
    {
      var childNodeName = childNodes.item(i).nodeName;
      
      if (xmlNode.selectNodes("./" + childNodeName).length > 1)
      {
        obj[xmlNode.nodeName][childNodeName] = new Array();
        obj[xmlNode.nodeName][childNodeName].push(ProcessNode(childNodes.item(i), obj[xmlNode.nodeName]));
      }
      else
      {
        obj[xmlNode.nodeName][childNodeName] = ProcessNode(childNodes.item(i), obj[xmlNode.nodeName]);
      }
    }
  }
  return obj;
}

function ProcessNodeOne(ANode)
{
  var FID, Attrs, i, Attr, ChildNodes;
  
  // Create a log folder for each node and activates the folder 
  FID = Log.CreateFolder(ANode.nodeName);
  Log.PushLogFolder(FID);

  // If the node value is not null, output it 
  if( aqObject.GetVarType(ANode.nodeValue) != 1) 
    Log.Message("Value: " + aqConvert.VarToStr(ANode.nodeValue));
       
  // Process node's attributes
  
  // Exclude helper nodes from processing
  if( ANode.nodeName.charAt(0) != "\#")
  {
    // Obtains the attributes collection and 
    // outputs the attributes to the log
    Attrs = ANode.attributes;
    for(i = 0; i < Attrs.length; i++)
    {
      Attr = Attrs.item(i);
      Log.Message("Attr " + Attr.nodeName + ": " + Attr.nodeValue); 
    }
  }
    
  // Obtains the collection of child nodes
  ChildNodes = ANode.childNodes;
  // Processes each node of the collection
  for(i = 0; i < ChildNodes.length; i++)
     ProcessNodeOne(ChildNodes.item(i)); 
  
  // Close the log folder
  Log.PopLogFolder();
}

// Output properties of the obj
// obj: the object to be parsed
// name: name of the object
function DumpObject(obj, name)
{
  var objType = Object.prototype.toString.call(obj);
    if (objType === "[object Array]")
    {
        Log.PushLogFolder(Log.CreateFolder(name == null ? objType : name));
    for (var i = 0; i < obj.length; i ++)
    {
      Log.PushLogFolder(Log.CreateFolder("Iteration<" + i + ">"));
      DumpObject(obj[i]);
      Log.PopLogFolder();
    }
    Log.PopLogFolder();
  }
  else if (typeof obj == "object")
  {
    if (obj == null)
    {
        Log.Message(name + " : " + obj);
    }
    else
    {
        var folder = Log.CreateFolder(name == null ? obj : name);
        Log.PushLogFolder(folder);
        for(var p in obj)
        {
          DumpObject(obj[p], p);
        }
        Log.PopLogFolder();
    }
  }
  else
  {
    Log.Message(name + " : " + obj);
  }
}
