# ----------------------------------
# Script to assist with device setup
# --------------------------------




# ---------- VARS ----------


$zipFile = "C:\Users\TylerPierce\Downloads\Acrobat_DC_Web_x64_WWMUI.zip"
$extractPath = "C:\Users\TylerPierce\Downloads\AdobeInstall"
$installer = Get-ChildItem -Path $extractPath -Filter "setup.exe" -Recurse | Select-Object -First 1



# ---------- METHODS ----------


# WORKS 
function removeApps {
    winget uninstall "Xbox TCUI"
    winget uninstall "Xbox Identity Provider"
}



# WORKS 
function downloadAdobe {
    
    # Target URL
    $url = "https://trials.adobe.com/AdobeProducts/APRO/Acrobat_HelpX/win32/Acrobat_DC_Web_x64_WWMUI.zip"

    # Downloading it
    Start-BitsTransfer -Source $url -Destination $zipFile
    Write-Host "Finished downloading Adobe"
}



function installAdobe {

    # Search for installer (setup.exe)

    if ($installer) {
        Write-Host "Found setup at: $($installer.FullName)"

        # Run installer 
        Start-Process $installer.FullName -ArgumentList "/sAll /quiet" -Wait

        Write-Host "Adobe instilation complete"
    }
    else {
        Write-Host "Unable to find setup.exe"
    }

}



# ---------- MAIN ----------

#downloadAdobe
#extractingAdobe
installAdobe









# ----- UNUSED FUNCTIONS -----


# WAS USED WHEN DOWNLOADING A ZIP, NOW DOWNLOADING EXE FILE INSTEAD
 function extractingAdobe {

    # Checks to see if folder exists, if it doesnt then makes it 
    if (!(Test-Path $extractPath)) {
        New-Item -ItemType Directory -Path $extractPath
    }

    # Run command 
    Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

}