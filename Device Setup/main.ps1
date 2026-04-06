# ----------------------------------
# Script to assist with device setup
# ----------------------------------


# TODO:
# - Can I change the power mode to best perfomance when plugged in?
# - Add other programs to remove, see pictures
# - Can I set myapps as a bookmark at least? 





# ---------- VARS ----------

$encompassURL = "https://download.elliemae.com/encompass/install/smartclient/enc360/EncompassDesktop.exe"
$downloadPath = "$env:USERPROFILE\Downloads"
$encompassFile = "$downloadPath\EncompassDesktop.exe"

# ---------- METHODS ----------



function setTimeZone {

    Set-TimeZone -Name "Eastern Standard Time"

}


# Do we want to use this? It block the ability to change it in the GUI
function setPowerPlan {

    powercfg /setactive SCHEME_MIN

}



function setSleepSetting {

    # Sets monitor to turn off after 2 hours
    powercfg /change monitor-timeout-ac 120
    # Sets computer to sleep after 2 hours
    powercfg /change standby-timeout-ac 120

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


# Do we want to do this? It locks out the user from changing it later.
function setEdgeHomepage {
    
    $homepageURL = "https://myapps.microsoft.com"

    $edgePoliciesPath = "HKCU:\SOFTWARE\Policies\Microsoft\Edge"

    # Create policy key if it doesn't exist
    New-Item -Path $edgePoliciesPath -Force | Out-Null

    # Get edge to open start page
    Set-ItemProperty -Path $edgePoliciesPath -Name "RestoreOnStartup" -Value 4

    # Make URL list key
    New-Item -Path "$edgePoliciesPath\RestoreOnStartupURLs" -Force | Out-Null

    # Set homepage URL
    Set-ItemProperty -Path "$edgePoliciesPath\RestoreOnStartupURLs" -Name "1" -Value $homepageURL
    
}


# Opens rename menu
function renameComputer {

    # Opens system menu when you can rename computer and see users name
    Start-Process "ms-settings:about"

    # Opens rename box but cant see users name 
    #Start-Process "SystemPropertiesComputerName"

}

# ---------- MAIN ----------

#installAdobe
#downloadEncompass
#installEncompass
#setTimeZone
#renameComputer
