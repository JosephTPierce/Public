# ----------------------------------
# Script to assist with device setup
# --------------------------------



# TODO:
# - Find a way to pin Outlook and teams to task bar
# - Find a way to pin Outlook and teams to start menu
# - Find a way to unpin items from taskbar
# - Find a way to unpin items from start menu
# - Find a way to open or sign into OneDrive
# - See if I can set homepage to myapps.microsoft.com in edge
# - See if we can open rename dialog at the end 



# ---------- VARS ----------

$encompassURL = "https://download.elliemae.com/encompass/install/smartclient/enc360/EncompassDesktop.exe"
$downloadPath = "$env:USERPROFILE\Downloads"
$encompassFile = "$downloadPath\EncompassDesktop.exe"

# ---------- METHODS ----------



function setTimeZone {

    Set-TimeZone -Name "Eastern Standard Time"

}



# Sets power plan to High Performance, doesnt allow user to change it in the future without PS... see if thats okay
function setPowerPlan {

    powercfg /setactive SCHEME_MIN

}



function setSleepSetting {

    # Sets monitor to turn off after 2 hours
    powercfg /change monitor-timeout-ac 120
    # Sets computer to sleep after 2 hours
    powercfg /change standby-timeout-ac 120

}


# ADD PROGRAMS TO REMOVE
function removeApps {

    winget uninstall "Xbox TCUI"
    winget uninstall "Xbox Identity Provider"

}



function installAdobe{

    winget install --id=Adobe.Acrobat.Reader.64-bit -e --silent --accept-package-agreements --accept-source-agreements

}



function downloadEncompass {

    Invoke-WebRequest $encompassURL -OutFile $encompassFile

}



function installEncompass {

    # Checks to see if file exists, then runs it 
    if(Test-Path $encompassFile) {
        Start-Process -FilePath $encompassFile -Wait
    } else {
        Write-Host "Encompass installer not found"
    }

}



# ---------- MAIN ----------

installAdobe
downloadEncompass
installEncompass
setTimeZone