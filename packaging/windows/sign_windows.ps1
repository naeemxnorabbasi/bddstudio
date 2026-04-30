param(
    [Parameter(Mandatory=$true)]
    [string]$BundleDir,

    [Parameter(Mandatory=$false)]
    [string]$CertPath,

    [Parameter(Mandatory=$false)]
    [string]$CertPassword,

    [Parameter(Mandatory=$false)]
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

# Sign Windows executables in the portable bundle.
#
# Option A: Use a PFX certificate:
#   powershell -ExecutionPolicy Bypass -File packaging/windows/sign_windows.ps1 `
#     -BundleDir release/BDDStudio-windows-x64 `
#     -CertPath C:\certs\codesign.pfx `
#     -CertPassword "..."
#
# Option B: Use a certificate already installed in the Windows certificate store:
#   adjust this script to use -Cert instead of -FilePath.
#
# You need Windows SDK SignTool installed.
# GitHub-hosted windows-latest usually has signtool in a Windows Kits path.

$ErrorActionPreference = "Stop"

$signtool = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter signtool.exe |
  Where-Object { $_.FullName -match "x64" } |
  Select-Object -First 1 -ExpandProperty FullName

if (-not $signtool) {
    throw "signtool.exe not found. Install Windows SDK."
}

$files = Get-ChildItem $BundleDir -Recurse -Include *.exe,*.dll

foreach ($f in $files) {
    Write-Host "Signing $($f.FullName)"
    if ($CertPath) {
        & $signtool sign /f $CertPath /p $CertPassword /fd SHA256 /tr $TimestampUrl /td SHA256 $f.FullName
    } else {
        & $signtool sign /a /fd SHA256 /tr $TimestampUrl /td SHA256 $f.FullName
    }
}
