# ----------------------------------
# Script to assist with device setup
# --------------------------------


# ---------- VARS ----------



# ---------- METHODS ----------


# WORKS 
function removeApps {
    winget uninstall "Xbox TCUI"
    winget uninstall "Xbox Identity Provider"
}



function installAdobe{
    winget install --id=Adobe.Acrobat.Reader.64-bit -e --silent --accept-package-agreements --accept-source-agreements
    Write-Host "Adobe Reader installed"
}


# ---------- MAIN ----------

installAdobe