param([string]$OutputRoot = (Join-Path $PSScriptRoot 'review-package'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$stickerPlan = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sticker-plan.json') -Raw | ConvertFrom-Json
$visualQa = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'visual-qa-20260914.json') -Raw | ConvertFrom-Json
$reworkById = @{}
foreach ($item in $visualQa.rework_candidates) { $reworkById[$item.id] = $item.reason }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$inventory = @{}
foreach ($asset in $stickerPlan.assets) {
  if ($asset.id -notmatch '^[a-z0-9-]+$') { throw 'Unsafe asset ID' }
  $source = Join-Path $PSScriptRoot ('unique/' + $asset.id + '.png')
  if (-not (Test-Path -LiteralPath $source)) { $inventory[$asset.id] = [ordered]@{id=$asset.id;subject=$asset.subject;status='missing'}; continue }
  $bitmap = [Drawing.Bitmap]::new($source)
  try {
    $corners = @($bitmap.GetPixel(0,0).A,$bitmap.GetPixel($bitmap.Width-1,0).A,$bitmap.GetPixel(0,$bitmap.Height-1).A,$bitmap.GetPixel($bitmap.Width-1,$bitmap.Height-1).A)
    $isTransparent = @($corners | Where-Object { $_ -gt 0 }).Count -eq 0
    $inventory[$asset.id] = [ordered]@{id=$asset.id;subject=$asset.subject;status=$(if($isTransparent){'alpha_verified'}else{'needs_alpha'});width=$bitmap.Width;height=$bitmap.Height;corner_alpha=$corners;sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash;source=$source}
  } finally { $bitmap.Dispose() }
}
$topicRows = @()
$cards = [Text.StringBuilder]::new()
$enc = {param($value) [System.Net.WebUtility]::HtmlEncode([string]$value)}
foreach ($topic in $stickerPlan.topics) {
  if ($topic.slug -notmatch '^[a-z0-9-]+$') { throw 'Unsafe topic slug' }
  $generated = 0; $alpha = 0
  $figures = [Text.StringBuilder]::new()
  foreach ($id in $topic.asset_ids) {
    $record = $inventory[$id]
    $imagePath = $null
    if ($record.status -ne 'missing') {
      $generated++
      $category = '_needs-alpha'
      if ($record.status -eq 'alpha_verified') { $alpha++; $category='stickers' }
      $imagePath = "$category/$($topic.slug)/$id.png"
      $destination = Join-Path $OutputRoot $imagePath
      New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
      if (Test-Path -LiteralPath $destination) {
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $record.sha256) { throw "Existing output differs: $destination" }
      } else { Copy-Item -LiteralPath $record.source -Destination $destination }
    }
    $statusText = switch($record.status){ 'alpha_verified' {'Có alpha'} 'needs_alpha' {'Cần sửa nền'} default {'Chưa tạo'} }
    $graphic = if($imagePath){'<img loading="lazy" src="'+(& $enc $imagePath)+'" alt="'+(& $enc $record.subject)+'">'}else{'<div class="placeholder">Chưa tạo</div>'}
    $dimensionsText = if($imagePath){'<small>'+ $record.width +' × '+ $record.height +' px</small>'}else{''}
    $qaText = if($reworkById.ContainsKey($id)){'<small title="'+(& $enc $reworkById[$id])+'">Cần chỉnh hình</small>'}else{''}
    [void]$figures.Append('<figure class="'+$record.status+'">'+$graphic+'<figcaption>'+(& $enc $id)+'<small>'+ $statusText +'</small>'+$dimensionsText+$qaText+'</figcaption></figure>')
    $topicRows += [pscustomobject]@{topic=$topic.slug;name_vi=$topic.name_vi;id=$id;subject=$record.subject;status=$record.status;file=$imagePath;sha256=$record.sha256;review_note=$reworkById[$id]}
  }
  [void]$cards.Append('<section data-search="'+(& $enc ($topic.slug+' '+$topic.name_vi+' '+($topic.asset_ids -join ' ')))+'"><h2>'+(& $enc $topic.name_vi)+' <small>'+$generated+'/8 hình · '+$alpha+' có alpha</small></h2><div class="grid">'+$figures.ToString()+'</div></section>')
}
$present = @($inventory.Values | Where-Object status -ne 'missing').Count
$ready = @($inventory.Values | Where-Object status -eq 'alpha_verified').Count
$summary = [ordered]@{updated_utc=[DateTime]::UtcNow.ToString('o');target_topics=50;target_slots=400;target_unique=390;prompt_target_dimensions=@(512,512);prompt_target_only=$true;scripted_resizing=$false;generated_unique=$present;alpha_verified_unique=$ready;needs_alpha_unique=($present-$ready);missing_unique=(390-$present);complete=$false;assets=@($inventory.Values | Sort-Object id);topic_slots=$topicRows}
$summary | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $OutputRoot 'progress.json') -Encoding utf8
$topicRows | Export-Csv -LiteralPath (Join-Path $OutputRoot 'topic-map.csv') -NoTypeInformation -Encoding utf8
$metadataRoot = Join-Path $OutputRoot '_metadata'
New-Item -ItemType Directory -Path $metadataRoot -Force | Out-Null
Get-ChildItem -LiteralPath $PSScriptRoot -File | Where-Object { $_.Extension -in @('.jsonl','.txt','.md') -or $_.Name -in @('sticker-plan.json','visual-qa-20260914.json') } | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $metadataRoot $_.Name) -Force}
$referenceCards = [Text.StringBuilder]::new()
$referenceFiles = @('8-Gardening/8-Gardening_1.png','2. Home appliance/68-Home Appliance_2.png','3_Flowers/Flower_3.png','Shirts/19_Shirts_1.png')
foreach ($referenceFile in $referenceFiles) {
  $referencePath = Join-Path 'C:/Users/sonng/OneDrive/Máy tính/Stickers' $referenceFile
  $referenceData = [Convert]::ToBase64String([IO.File]::ReadAllBytes($referencePath))
  [void]$referenceCards.Append('<figure><img src="data:image/png;base64,'+$referenceData+'" alt="Mẫu gốc"><figcaption>Mẫu gốc · '+(& $enc $referenceFile)+'</figcaption></figure>')
}
$html = @'
<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NewStickers — tiến độ</title><style>
*{box-sizing:border-box}body{margin:0;font:15px system-ui,sans-serif;background:#f6f0e8;color:#493f34}header{padding:28px 4vw;position:sticky;top:0;background:#f6f0e8ee;backdrop-filter:blur(12px);z-index:2;border-bottom:1px solid #dbcfc0}h1{margin:0 0 8px}p{margin:6px 0 14px}input,button{font:inherit;padding:10px 14px;border:1px solid #c9bba8;border-radius:9px;background:white}input{width:min(480px,70%)}button{cursor:pointer}main{padding:12px 4vw 50px}section{margin:28px 0 40px}h2{font-size:22px}small{font-size:12px;font-weight:400;display:block;color:#817060;margin-top:5px}.grid{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:12px}figure{margin:0;border:1px solid #e1d5c6;background:#fffdfa;border-radius:14px;overflow:hidden}figure img,.placeholder{width:100%;height:160px;object-fit:contain;padding:8px;background:var(--art-bg,#eae0d2)}.placeholder{display:grid;place-items:center;color:#ac9e8d;font-size:12px}figcaption{padding:10px;font-size:11px;word-break:break-word}.needs_alpha small{color:#ad632c}.alpha_verified small{color:#467246}.missing{opacity:.55}body.dark{--art-bg:#363b40}@media(max-width:1000px){.grid{grid-template-columns:repeat(4,1fr)}}@media(max-width:550px){.grid{grid-template-columns:repeat(2,1fr)}}
</style><header><h1>NewStickers</h1><p>Đang thực hiện · __PRESENT__/390 hình riêng · __READY__ hình có alpha · mục tiêu 50 chủ đề, 8 hình/chủ đề.</p><input id="search" placeholder="Tìm chủ đề hoặc mã sticker"><button id="theme">Đổi nền xem ảnh</button></header><main><details style="margin-top:20px"><summary>Mẫu gốc để đối chiếu nét vẽ và độ tương phản</summary><p>Tham chiếu từ folder Stickers ngoài desktop.</p><div class="grid">__REFERENCES__</div></details>__CARDS__</main><script>document.querySelector('#search').addEventListener('input',e=>{let q=e.target.value.toLocaleLowerCase('vi');document.querySelectorAll('section').forEach(s=>s.hidden=!s.dataset.search.toLocaleLowerCase('vi').includes(q))});document.querySelector('#theme').onclick=()=>document.body.classList.toggle('dark');</script></html>
'@
$html.Replace('__PRESENT__',[string]$present).Replace('__READY__',[string]$ready).Replace('__REFERENCES__',$referenceCards.ToString()).Replace('__CARDS__',$cards.ToString()) | Set-Content -LiteralPath (Join-Path $OutputRoot 'index.html') -Encoding utf8
@"
# NewStickers — đang thực hiện

Đã tạo $present/390 hình riêng cho kế hoạch 50 chủ đề, tổng 400 vị trí. Có $ready hình đã kiểm tra alpha ở bốn góc. Đây chưa phải bộ hoàn tất.

Mở index.html để xem toàn bộ tiến độ. Thư mục stickers chứa PNG có alpha; _needs-alpha chứa bản vẽ cần sửa nền, chưa dùng trực tiếp trong game. Không coi ô caro vẽ trong ảnh là nền trong suốt. Cần kiểm tra mỹ thuật và viền ảnh khi thu nhỏ trước khi tích hợp.

Phong cách chỉ lấy từ C:/Users/sonng/OneDrive/Máy tính/Stickers/. Mẫu tổ ong cũ tương phản cao đã bị loại. _metadata lưu kế hoạch, prompt và ghi chú. topic-map.csv ghi hình dùng chung giữa hai chủ đề.

Target trong prompt cho ảnh tạo tiếp theo là 512 × 512 theo yêu cầu. Không resize bằng script. Kích thước thực tế có thể khác target và được ghi trong progress.json.
"@ | Set-Content -LiteralPath (Join-Path $OutputRoot 'README.vi.md') -Encoding utf8
[pscustomobject]@{generated=$present;alpha_verified=$ready;needs_alpha=$present-$ready;missing=390-$present;package=$OutputRoot} | ConvertTo-Json -Compress
