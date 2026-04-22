# ----------------------------------
# Script to assist with device setup
# ----------------------------------



# What needs to be done manually:
# - Sign in to OneDrive
# - Pin/unpin apps to taskbar/start menu
# - Set homepage in Edge
# - Set encompass instanceID
# - Set powermode/sleep settings 
# - Enter in laptop name (script opens menu but does not enter name for you)
# - Add device to inventory



# ---------- VARS --------------

$encompassURL = "https://download.elliemae.com/encompass/install/smartclient/enc360/EncompassDesktop.exe"
$downloadPath = "$env:USERPROFILE\Downloads"
$encompassFile = "$downloadPath\EncompassDesktop.exe"


# ---------- METHODS ----------


function setTimeZone {

    Set-TimeZone -Name "Eastern Standard Time"

}



function removeApps {

    # List of apps to remove

    winget uninstall "Xbox TCUI"
    winget uninstall "Xbox Identity Provider"
    winget uninstall "Xbox"
    winget uninstall "Game Bar"
    winget uninstall --id McAfee.wps -e 
    winget uninstall --id McAfeeWPSSparsePackage -e 
    winget uninstall "Lenovo Vantage"
    winget uninstall "Lenovo Vantage Service"
    winget uninstall "Lenovo Smart Meeting Components"
    winget uninstall "Lenovo Commercial Vantage"
    winget uninstall "Lenovo Smart Meeting"
    winget uninstall "Lenovo Smart Noise Cancellation"
    winget uninstall "Elevoc Smart Noise Cancellation Settings" #Lenovo Smart Noise Cancellation
    winget uninstall "WebAdvisor by McAfee"
    winget uninstall "Feedback Hub"
    winget uninstall "Microsoft Journal"
    winget uninstall "Microsoft Family"
    winget uninstall "Smart Connect"

}



function installAdobe{

    winget install --id=Adobe.Acrobat.Reader.64-bit -e --silent --accept-package-agreements --accept-source-agreements --source winget

}



function downloadEncompass {

    Invoke-WebRequest $encompassURL -OutFile $encompassFile

}



function installEncompass {

    # Checks to see if file exists, then runs it 
    if(Test-Path $encompassFile) {
        Start-Process -FilePath $encompassFile -Verb RunAs -Wait
    } else {
        Write-Host "Encompass installer not found"
    }

}


# Stole AJs code for this -- see if it still lets the user change afterwards
function setPowerSettings {
    
    # Plugged-in only (AC)

    powercfg /change monitor-timeout-ac 15
    powercfg /change standby-timeout-ac 0


    # Lid close = Do nothing (AC only)

    $scheme = (powercfg -getactivescheme) -replace ".*GUID:\s*([a-fA-F0-9\-]+).*",'$1'
    powercfg -setacvalueindex $scheme 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
    powercfg -S $scheme
    
}


# Opens rename menu
function renameComputer {

    # Opens system menu where you can rename
    Start-Process "ms-settings:about"

    # Opens rename box but cant see users name 
    #Start-Process "SystemPropertiesComputerName.exe"

}



# ---------- MAIN ----------


#installAdobe
#setTimeZone
#removeApps
#downloadEncompass
#installEncompass
#renameComputer
setPowerSettings
