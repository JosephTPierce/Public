# ----------------------------------
# Script to assist with device setup
# ----------------------------------



# TODO:
# - Find a way to pin Outlook and teams to task bar
# - Find a way to pin Outlook and teams to start menu
# - Find a way to unpin items from taskbar
# - Find a way to unpin items from start menu

# - Find a way to open or sign into OneDrive -- cant automate 
# - See if I can set homepage to myapps.microsoft.com in edge -- kinda works. Could just open it instad



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

    # Definete removal

    winget uninstall "Xbox TCUI"
    winget uninstall "Xbox Identity Provider"
    winget uninstall "Xbox"
    winget uninstall "Game Bar"


    # possible removal 

    winget uninstall "Lenovo Vantage Service"
    winget uninstall "Lenovo Commercial Vantage"
    winget uninstall "Xbox Identity Provider"

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
