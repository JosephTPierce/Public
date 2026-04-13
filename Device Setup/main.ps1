# ----------------------------------
# Script to assist with device setup
# ----------------------------------



# ---------- VARS ----------

$encompassURL = "https://download.elliemae.com/encompass/install/smartclient/enc360/EncompassDesktop.exe"
$downloadPath = "$env:USERPROFILE\Downloads"
$encompassFile = "$downloadPath\EncompassDesktop.exe"

# ---------- METHODS ----------



function setTimeZone {

    Set-TimeZone -Name "Eastern Standard Time"

}


# What happens if you try to remove an app that doesnt exist?
function removeApps {

    # List of apps to remove

    winget uninstall "Xbox TCUI"
    winget uninstall "Xbox Identity Provider"
    winget uninstall "Xbox"
    winget uninstall "Game Bar"
    winget uninstall "McAfee"
    winget uninstall "Lenovo Vantage Service"
    winget uninstall "Lenovo Smart Meeting Components"
    winget uninstall "Lenovo Commercial Vantage"
    winget uninstall "WebAdvisor by McAfee"
    winget uninstall "Lenovo Now"
    winget uninstall "Lenovo Vantage"
    winget uninstall "Lenovo Smart Meeting"

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
        Start-Process -FilePath $encompassFile -Wait
    } else {
        Write-Host "Encompass installer not found"
    }

}



# Opens rename menu
function renameComputer {

    # Opens system menu when you can rename computer and see users name
    Start-Process "ms-settings:about"

    # Opens rename box but cant see users name 
    #Start-Process "SystemPropertiesComputerName"

}



# ---------- MAIN ----------

#removeApps
#installAdobe
#downloadEncompass
#installEncompass
#setTimeZone
#renameComputer
