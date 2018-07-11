$PREBUILD_SNAPSHOT_NAME = "prebuild"
$SNAPSHOTFAILURE        = "TestFailed"
$SERVER                 = $null
$ESX_VM_NAME            = ""
$SleepTime              = 15
$TimeOut                = 600
#VM Object return from get-vm -server "$ESX_NAME"  
#assum that VM name is start with $COMPUTER_NAME 
$G_VM                   = $null

add-pssnapin vmware.vimautomation.core -ErrorAction:silentlycontinue

#vSphere PowerCLI reference
#http://www.vmware.com/support/developer/PowerCLI/

function DeletePrebuildSnapshot()
{
   write-host("    Getting prebuild snapshots and delete it")

   $lstSnapshots = Get-Snapshot -VM $G_VM 

   foreach ($snapshot in $lstSnapshots)
   {    
        write-host("    Shapshot: " + $snapshot.Name)
        if ($snapshot.Name.Contains($PREBUILD_SNAPSHOT_NAME))
		{
		    Remove-Snapshot -Snapshot $snapshot -confirm:$false
		}
   }
}

function DeleteFailedSnapshots()
{
    write-host("In DeleteFailedSnapshots function")
    $KeepNoOfFailedSnapshots = 2
    $i=0    
    write-host("    Getting all snapshots and sort by created date")
    $lstSnapshots = Get-Snapshot -VM $G_VM | Sort-Object Created -Descending
    foreach ($snapshot in $lstSnapshots)
    {       
       write-host("    Shapshot: " + $snapshot.Name)
       if ($snapshot.Name.Contains($SNAPSHOTFAILURE))
       {                      
           if($i -ge $KeepNoOfFailedSnapshots)
           {
                write-host("    Deleting snapshot $snapshot") 
                Remove-Snapshot -Snapshot $snapshot -confirm:$false # Delete snapshot 
           }
           $i++
       }
    }    
}

function StartVM()
{   
    write-host("StartVM") 
    $vm = get-vm -Name $ESX_VM_NAME
    if ($vm -eq $null)
    {
	    write-host("PowerShell can not find the virtual machine "+$ESX_VM_NAME) 
		ShellExit 1
    }     
    
	#If prebuild snapshot is created while the VM is powered on, revert snapshot to prebuild will actuall start the VM to PoweredOn state
	if ($vm.PowerState -eq "PoweredOn")
    {
	    write-host($ESX_VM_NAME +" is already in PoweredOn state.")
        return 		
    }	

     write-host("    Powering up $ESX_VM_NAME")
	 write-host("    Timeout:$TimeOut")
     $vm = Start-VM $vm
		
     #By default wait for 10 mins at most
	 ipconfig /flushdns
     for($i=1; $i -le $TimeOut/$SleepTime; $i++)
     {
         write-host("    Checking whether " + $ESX_VM_NAME   + " is on the network....$i" )
         $OSStarted = Test-Connection $ESX_VM_NAME  -count 1 -Quiet
         if ($OSStarted -eq $True)
         {
             write-host($ESX_VM_NAME +" is on the network")
			 return 
         }            
         Start-Sleep -Second $SleepTime         
     }     
}

function ShutdownVM()
{
	if ($G_VM.PowerState -eq "PoweredOff")
    {
        write-host("$ESX_VM_NAME is already powered off.")
		ShellExit 0 
	}
	write-host("Shutting down $ESX_VM_NAME...")
	Shutdown-VMGuest -VM $G_VM -Confirm:$false
	
	for($i=1; $i -le $TimeOut/$SleepTime; $i++)
	{
		$G_VM = Get-VM -Name $ESX_VM_NAME
		write-host($G_VM.PowerState)
		if ($G_VM.PowerState -eq "PoweredOff")
		{
			write-host("$ESX_VM_NAME power off completed.")
			ShellExit 0
		}       
		Start-Sleep -Second $SleepTime         
	}
	# If VM is not powered off
	ShellExit 1
}

function RestartVM()
{
	if ($G_VM -eq $null)
    {
	    write-host("PowerShell can not find the virtual machine "+$ESX_VM_NAME) 
		ShellExit 1
    }
	
	if ($G_VM.PowerState -eq "PoweredOff")
	{
		StartVM
	}
	else
	{
		write-host("Begin to restart $ESX_VM_NAME")
		Restart-VM -VM $G_VM
	}
}

function CreatePrebuildSnapshot()
{    
    write-host("CreatePrebuildSnapshot")
    write-host("    Creating $PREBUILD_SNAPSHOT_NAME snapshot")
    New-Snapshot -Name $PREBUILD_SNAPSHOT_NAME -VM $G_VM
}

function RevertSnapshot()
{               
    write-host("RevertSnapshot")
    write-host("    Looking for $PREBUILD_SNAPSHOT_NAME snapshot")
    $vm = get-vm -Name $ESX_VM_NAME    
    $Snapshots = Get-Snapshot -Name $PREBUILD_SNAPSHOT_NAME -VM $vm | Sort-Object Created -descending 
    
    if ($Snapshots -ne $null)
    {
        write-host("    $PREBUILD_SNAPSHOT_NAME  found")
        $i = 0;
        foreach ($Snapshot in $Snapshots)
        {
            if ($i -eq 0)
            {
			    write-host("    Reverting snapshot to prebuild")
                set-vm -VM $vm -snapshot $Snapshot -confirm:$false    # Revert snapshot
                $i++;
            }  			
        }
		if($i -gt 1)
		{
		    write-host("    Warning: Found $i prebuild snapshots.")
		}
    } 
	else
	{
	    write-host("PowerShell can not found prebuild snapshot. Exit 401")
		ShellExit 401
	}
}

function CheckPoweredOff()
{
    while($True)
	{
       $G_VM = get-vm -Name $ESX_VM_NAME 
	   if($G_VM.PowerState -eq "PoweredOff")
	   {
	        write-host($ESX_VM_NAME+" has already powered off")
			break
	   
	   }
	   start-sleep -Second 3
	}
}

function GetVMPoweredStatus()
{
    $G_VM = get-vm -Name $ESX_VM_NAME 
	if($G_VM.PowerState -eq "PoweredOff")
	{
	   write-host($ESX_VM_NAME+" is in the powered off state")
	   ShellExit 0
	}else{
	   write-host($ESX_VM_NAME+" is in the powered on state")
	   ShellExit 1
	}
}

function Setup()
{
    write-host("In Setup function")
    if ($G_VM.PowerState -ne "PoweredOff")
    {
		write-host($ESX_VM_NAME +" is not in PoweredOff state,please manually check it whether used by another job.")
        ShellExit 402
	}
    DeleteFailedSnapshots
    RevertSnapshot
    StartVM    
}    

function SnapshotFailure()
{
    $failureDateTime =  get-date -format "dd-MM-yyyy_HH-mm-ss" 
    $SnapshotFailureName =  $SNAPSHOTFAILURE + " (" + $failureDateTime + ")" 
    write-host("Creating failure snapshot " + $SnapshotFailureName)
    
    New-Snapshot -Name $SnapshotFailureName -Memory:$true -VM $ESX_VM_NAME -Server $Server
}

function ShellExit($returnCode)
{
	write-host("PowerShell exit $returnCode")
	exit $returnCode
}

# Main entry point

if ($args.length -eq 0) { write-host ("Missing argument - stop|start needed") } 

write-host "Command:" $args[0]

$ESX_VM_NAME = $args[1]
$ESX_NAME  = $args[2]
$ESX_USERNAME = $args[3]
$ESX_PASSWORD = $args[4]
if( $args[5] -ne $null)
{
   $TimeOut = $args[5]
}
write-host "Connecting to ESX $ESX_NAME as $ESX_USERNAME ..."
$SERVER = connect-viserver -server "$ESX_NAME" -user "$ESX_USERNAME" -password "$ESX_PASSWORD" -ErrorAction:stop
write-host "ESX_VM_NAME: $ESX_VM_NAME"
$G_VM = get-vm -Name $ESX_VM_NAME 
switch ($args[0])
{
    "start" { Setup }
	"shutdown" { ShutdownVM }
	"restart" { RestartVM }
    "snapshotfailure" { SnapshotFailure }
	"deletefailedsnapshots" { DeleteFailedSnapshots }
    "createprebuild" { CreatePrebuildSnapshot }
    "deleteprebuild" { DeletePrebuildSnapshot }
	"CheckPoweredOff" { CheckPoweredOff }
	"GetVMPoweredStatus" { GetVMPoweredStatus }
    "default" { write-host ("Unknown argument: $args[0]") }
}

ShellExit 0


