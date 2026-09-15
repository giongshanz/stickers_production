param(
  [Parameter(Mandatory=$true)][string]$Source,
  [Parameter(Mandatory=$true)][string]$AssetId
)
$ErrorActionPreference = 'Stop'
if ($AssetId -notmatch '^[a-z0-9][a-z0-9-]+$') { throw 'Invalid asset ID' }
$productionRoot = $PSScriptRoot
$uniqueRoot = Join-Path $productionRoot 'unique'
New-Item -ItemType Directory -Path $uniqueRoot -Force | Out-Null
$stickerDestination = Join-Path $uniqueRoot ($AssetId + '.png')
if (Test-Path -LiteralPath $stickerDestination) { throw "Asset already exists: $AssetId" }
Copy-Item -LiteralPath $Source -Destination $stickerDestination
Add-Type -AssemblyName System.Drawing
$stickerImage = [System.Drawing.Bitmap]::new($stickerDestination)
try {
  [pscustomobject]@{
    id=$AssetId
    file=$stickerDestination
    width=$stickerImage.Width
    height=$stickerImage.Height
    pixelFormat=$stickerImage.PixelFormat.ToString()
    cornerAlpha=@($stickerImage.GetPixel(0,0).A,$stickerImage.GetPixel($stickerImage.Width-1,0).A,$stickerImage.GetPixel(0,$stickerImage.Height-1).A,$stickerImage.GetPixel($stickerImage.Width-1,$stickerImage.Height-1).A)
  } | ConvertTo-Json -Compress
} finally { $stickerImage.Dispose() }
