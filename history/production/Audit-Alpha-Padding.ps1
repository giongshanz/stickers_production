$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$stickerAssemblyReferences = if ($PSVersionTable.PSEdition -eq 'Desktop') { @('System.Drawing') } else { @([Drawing.Bitmap].Assembly.Location,[Drawing.Rectangle].Assembly.Location,'System.Runtime','System.Runtime.InteropServices','System.Private.Windows.GdiPlus','System.Private.Windows.Core') }
Add-Type -ReferencedAssemblies $stickerAssemblyReferences -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class StickerAlphaAudit {
  public static int[] Scan(string path) {
    using (Bitmap bitmap = new Bitmap(path)) {
      if (!Image.IsAlphaPixelFormat(bitmap.PixelFormat)) return null;
      Rectangle rect = new Rectangle(0, 0, bitmap.Width, bitmap.Height);
      BitmapData data = bitmap.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
      try {
        int stride = Math.Abs(data.Stride);
        byte[] pixels = new byte[stride * bitmap.Height];
        Marshal.Copy(data.Scan0, pixels, 0, pixels.Length);
        int left = bitmap.Width, top = bitmap.Height, right = -1, bottom = -1;
        int transparent = 0, partial = 0, opaque = 0;
        for (int y = 0; y < bitmap.Height; y++) for (int x = 0; x < bitmap.Width; x++) {
          byte alpha = pixels[y * stride + x * 4 + 3];
          if (alpha == 0) transparent++; else if (alpha == 255) opaque++; else partial++;
          if (alpha >= 128) { left = Math.Min(left, x); top = Math.Min(top, y); right = Math.Max(right, x); bottom = Math.Max(bottom, y); }
        }
        return new int[] {bitmap.Width, bitmap.Height, left, top, bitmap.Width - 1 - right, bitmap.Height - 1 - bottom, transparent, partial, opaque};
      } finally { bitmap.UnlockBits(data); }
    }
  }
}
'@
$rows = foreach ($stickerFile in Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'unique') -Filter '*.png' -File) {
  $scan = [StickerAlphaAudit]::Scan($stickerFile.FullName)
  if ($null -eq $scan) { continue }
  $minPadding = ($scan[2..5] | Measure-Object -Minimum).Minimum
  [pscustomobject]@{
    id=$stickerFile.BaseName
    dimensions=@($scan[0],$scan[1])
    padding_left_top_right_bottom=$scan[2..5]
    transparent_pixels=$scan[6]
    partial_alpha_pixels=$scan[7]
    opaque_pixels=$scan[8]
    review_edge=($minPadding -lt 0.02*[Math]::Min($scan[0],$scan[1]))
  }
}
$rows | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'alpha-padding-audit.json') -Encoding utf8
$rows | Where-Object review_edge | Select-Object id,padding_left_top_right_bottom | ConvertTo-Json -Compress
