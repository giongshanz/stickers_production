#requires -Version 7.0
<#!
Copy-only packaging: reads original PNGs and never resizes or edits artwork.
Final packaging is refused unless the complete plan and all source PNGs validate.
Use -ValidateOnly for an honest inventory while generation is still in progress.
!#>
[CmdletBinding()]
param(
    [string]$ProductionRoot = $PSScriptRoot,
    [string]$PlanPath = '',
    [string]$DeliveryRoot = '',
    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'
$productionPath = [IO.Path]::GetFullPath($ProductionRoot)
if (-not $PlanPath) { $PlanPath = Join-Path $productionPath 'sticker-plan.json' }
if (-not $DeliveryRoot) { $DeliveryRoot = Join-Path $productionPath 'delivery' }
$planFile = [IO.Path]::GetFullPath($PlanPath)
$deliveryPath = [IO.Path]::GetFullPath($DeliveryRoot)
$uniquePath = Join-Path $productionPath 'unique'
$validationPath = Join-Path $productionPath 'packaging-validation.json'

function Write-JsonFile([object]$Value, [string]$Path) {
    $Value | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Get-PngInfo([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $reader = [IO.BinaryReader]::new($stream)
    try {
        $signature = $reader.ReadBytes(8)
        if ([Convert]::ToHexString($signature) -ne '89504E470D0A1A0A') {
            throw 'File does not have a PNG signature.'
        }
        $width = 0; $height = 0; $bitDepth = 0; $colorType = -1
        $hasAlphaChannel = $false; $hasTransparencyChunk = $false; $foundEnd = $false
        while ($stream.Position -lt $stream.Length) {
            $lengthBytes = $reader.ReadBytes(4)
            if ($lengthBytes.Length -ne 4) { throw 'Truncated PNG chunk length.' }
            [Array]::Reverse($lengthBytes)
            $chunkLength = [BitConverter]::ToUInt32($lengthBytes, 0)
            $typeBytes = $reader.ReadBytes(4)
            if ($typeBytes.Length -ne 4) { throw 'Truncated PNG chunk type.' }
            $chunkType = [Text.Encoding]::ASCII.GetString($typeBytes)
            if (($stream.Position + [long]$chunkLength + 4) -gt $stream.Length) {
                throw 'PNG chunk extends beyond the file.'
            }
            if ($chunkType -eq 'IHDR') {
                if ($chunkLength -ne 13) { throw 'Invalid PNG header length.' }
                $header = $reader.ReadBytes(13)
                $widthBytes = $header[0..3]; [Array]::Reverse($widthBytes)
                $heightBytes = $header[4..7]; [Array]::Reverse($heightBytes)
                $width = [BitConverter]::ToUInt32([byte[]]$widthBytes, 0)
                $height = [BitConverter]::ToUInt32([byte[]]$heightBytes, 0)
                $bitDepth = $header[8]; $colorType = $header[9]
                $hasAlphaChannel = $colorType -in @(4, 6)
            } else {
                if ($chunkType -eq 'tRNS') { $hasTransparencyChunk = $true }
                [void]$stream.Seek([long]$chunkLength, [IO.SeekOrigin]::Current)
            }
            [void]$reader.ReadBytes(4)
            if ($chunkType -eq 'IEND') { $foundEnd = $true; break }
        }
        if (-not $foundEnd -or $width -eq 0 -or $height -eq 0) {
            throw 'PNG is missing a valid header or ending chunk.'
        }
    } finally {
        $reader.Dispose(); $stream.Dispose()
    }
    # Decode read-only as an additional integrity check. No bitmap is saved.
    $decodedImage = [Drawing.Image]::FromFile($Path)
    try {
        if ($decodedImage.Width -ne $width -or $decodedImage.Height -ne $height) {
            throw 'PNG header dimensions disagree with the decoded image.'
        }
    } finally { $decodedImage.Dispose() }
    return [ordered]@{
        width = $width; height = $height; bit_depth = $bitDepth
        png_color_type = $colorType; alpha_channel_present = $hasAlphaChannel
        transparency_chunk_present = $hasTransparencyChunk
        transparency_note = 'Channel/chunk presence only; visible transparency and art quality require visual QA.'
    }
}

function Html([object]$Value) { return [Net.WebUtility]::HtmlEncode([string]$Value) }

if (-not (Test-Path -LiteralPath $planFile -PathType Leaf)) {
    throw "Plan not found: $planFile"
}
Add-Type -AssemblyName System.Drawing
$plan = Get-Content -LiteralPath $planFile -Raw | ConvertFrom-Json
$errors = [Collections.Generic.List[string]]::new()
$warnings = [Collections.Generic.List[string]]::new()
$assetsById = @{}
$usageById = @{}
$topicsBySlug = @{}
$safeName = '^[a-z0-9]+(?:[-_][a-z0-9]+)*$'

if (@($plan.topics).Count -ne 50) { $errors.Add('Plan must contain exactly 50 topics.') }
if (@($plan.assets).Count -eq 0) { $errors.Add('Plan has no assets.') }
foreach ($asset in @($plan.assets)) {
    $assetId = [string]$asset.id
    if ($assetId -cnotmatch $safeName) { $errors.Add("Unsafe or invalid asset id: $assetId"); continue }
    if ($assetsById.ContainsKey($assetId)) { $errors.Add("Duplicate asset id: $assetId"); continue }
    if (-not $asset.subject) { $errors.Add("Asset has no subject: $assetId") }
    $assetsById[$assetId] = $asset
    $usageById[$assetId] = [Collections.Generic.List[string]]::new()
}
foreach ($topic in @($plan.topics)) {
    $topicSlug = [string]$topic.slug
    if ($topicSlug -cnotmatch $safeName) { $errors.Add("Unsafe or invalid topic slug: $topicSlug"); continue }
    if ($topicsBySlug.ContainsKey($topicSlug)) { $errors.Add("Duplicate topic slug: $topicSlug"); continue }
    $topicsBySlug[$topicSlug] = $topic
    if (-not $topic.name_vi) { $errors.Add("Topic has no Vietnamese name: $topicSlug") }
    $ids = @($topic.asset_ids)
    if ($ids.Count -lt 8) { $errors.Add("Topic has fewer than 8 planned assets: $topicSlug") }
    if (@($ids | Select-Object -Unique).Count -ne $ids.Count) { $errors.Add("Topic repeats an asset id: $topicSlug") }
    foreach ($assetId in $ids) {
        if (-not $assetsById.ContainsKey([string]$assetId)) {
            $errors.Add("Unknown asset '$assetId' in topic '$topicSlug'.")
        } else { $usageById[[string]$assetId].Add($topicSlug) }
    }
}
$declaredShares = @{}
foreach ($shared in @($plan.shared_assets)) {
    $sharedId = [string]$shared.id
    if ($declaredShares.ContainsKey($sharedId)) { $errors.Add("Duplicate shared asset declaration: $sharedId"); continue }
    $declaredShares[$sharedId] = $shared
    if (-not $usageById.ContainsKey($sharedId)) { $errors.Add("Shared asset does not exist: $sharedId"); continue }
    $declaredTopics = @($shared.topic_slugs | Sort-Object -Unique)
    $actualTopics = @($usageById[$sharedId] | Sort-Object -Unique)
    if ($declaredTopics.Count -ne 2 -or ($declaredTopics -join '|') -ne ($actualTopics -join '|')) {
        $errors.Add("Shared asset must match exactly two actual topic usages: $sharedId")
    }
}
foreach ($assetId in $assetsById.Keys) {
    $usageCount = @($usageById[$assetId] | Select-Object -Unique).Count
    if ($usageCount -eq 0) { $errors.Add("Unused asset in plan: $assetId") }
    if ($usageCount -gt 2) { $errors.Add("Asset used by more than two topics: $assetId") }
    if ($usageCount -eq 2 -and -not $declaredShares.ContainsKey($assetId)) {
        $errors.Add("Shared asset is missing from shared_assets: $assetId")
    }
}

$inventory = [Collections.Generic.List[object]]::new()
$inventoryById = @{}
$missingIds = [Collections.Generic.List[string]]::new()
foreach ($asset in @($plan.assets)) {
    $assetId = [string]$asset.id
    if ($assetId -cnotmatch $safeName -or $inventoryById.ContainsKey($assetId)) { continue }
    $sourcePath = Join-Path $uniquePath "$assetId.png"
    $entry = [ordered]@{
        id = $assetId; subject = $asset.subject; source_relative = "unique/$assetId.png"
        source_absolute = $sourcePath; topic_slugs = @($usageById[$assetId])
        status = 'missing'; sha256 = $null; bytes = $null; png = $null
    }
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        $missingIds.Add($assetId)
    } else {
        try {
            $entry.png = Get-PngInfo $sourcePath
            $entry.sha256 = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $entry.bytes = (Get-Item -LiteralPath $sourcePath).Length
            $entry.status = 'valid'
            if (-not $entry.png.alpha_channel_present -and -not $entry.png.transparency_chunk_present) {
                $warnings.Add("PNG has no transparency channel/chunk: $assetId")
            }
        } catch {
            $entry.status = 'invalid'
            $entry.error = $_.Exception.Message
            $errors.Add("Invalid PNG '$assetId': $($_.Exception.Message)")
        }
    }
    $inventory.Add([pscustomobject]$entry)
    $inventoryById[$assetId] = [pscustomobject]$entry
}
if ($missingIds.Count -gt 0) { $errors.Add("Missing source PNGs: $($missingIds.Count). See missing_asset_ids in the validation report.") }
$topicChecks = @(
    foreach ($topic in @($plan.topics)) {
        $available = @($topic.asset_ids | Where-Object { $inventoryById.ContainsKey([string]$_) -and $inventoryById[[string]$_].status -eq 'valid' }).Count
        if ($available -lt 8) { $errors.Add("Topic '$($topic.slug)' has only $available valid source PNGs; at least 8 are required.") }
        [ordered]@{ slug = $topic.slug; name_vi = $topic.name_vi; planned = @($topic.asset_ids).Count; valid_pngs = $available }
    }
)
foreach ($duplicate in @($inventory | Where-Object status -eq 'valid' | Group-Object sha256 | Where-Object Count -gt 1)) {
    $warnings.Add("Different source ids have identical PNG bytes: $($duplicate.Group.id -join ', ')")
}
if (Test-Path -LiteralPath $uniquePath -PathType Container) {
    foreach ($extraFile in Get-ChildItem -LiteralPath $uniquePath -File -Filter '*.png') {
        if (-not $assetsById.ContainsKey($extraFile.BaseName)) { $warnings.Add("Unplanned PNG excluded: $($extraFile.Name)") }
    }
}
$report = [ordered]@{
    generated_utc = [DateTime]::UtcNow.ToString('o'); complete = ($errors.Count -eq 0)
    plan_path = $planFile; source_directory = $uniquePath; planned_topics = @($plan.topics).Count
    planned_unique_assets = @($plan.assets).Count; valid_unique_pngs = @($inventory | Where-Object status -eq 'valid').Count
    planned_topic_slots = (@($plan.topics | ForEach-Object { @($_.asset_ids).Count }) | Measure-Object -Sum).Sum
    missing_asset_ids = @($missingIds); errors = @($errors); warnings = @($warnings)
    topics = $topicChecks; assets = @($inventory)
}
Write-JsonFile $report $validationPath
if ($ValidateOnly) {
    Write-Output "Validation report: $validationPath"
    Write-Output "Complete: $($report.complete); valid unique PNGs: $($report.valid_unique_pngs)/$($report.planned_unique_assets); errors: $($errors.Count)"
    if ($errors.Count -gt 0) { exit 2 }
    exit 0
}
if ($errors.Count -gt 0) { throw "Packaging refused: $($errors.Count) validation errors. See $validationPath" }

# Require a new workspace destination. Existing delivery folders are preserved.
$productionPrefix = $productionPath.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $deliveryPath.StartsWith($productionPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'DeliveryRoot must resolve to a child directory inside ProductionRoot.'
}
if (Test-Path -LiteralPath $deliveryPath) { throw "Delivery already exists; choose another -DeliveryRoot: $deliveryPath" }
$stagingPath = Join-Path $productionPath ('.delivery-staging-' + [Guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $stagingPath)
$metadataPath = Join-Path $stagingPath 'metadata'
[void](New-Item -ItemType Directory -Path $metadataPath)
$rows = [Collections.Generic.List[object]]::new()
$cards = [Text.StringBuilder]::new()
foreach ($topic in $plan.topics) {
    $topicPath = Join-Path $stagingPath $topic.slug
    [void](New-Item -ItemType Directory -Path $topicPath)
    [void]$cards.AppendLine('<section class="topic" data-search="' + (Html ($topic.name_vi + ' ' + $topic.slug)) + '"><h2>' + (Html $topic.name_vi) + '</h2><p class="topic-slug">' + (Html $topic.slug) + '</p><div class="stickers">')
    foreach ($assetId in $topic.asset_ids) {
        $source = $inventoryById[[string]$assetId]
        $fileRelative = "$($topic.slug)/$assetId.png"
        $copiedPath = Join-Path $topicPath "$assetId.png"
        Copy-Item -LiteralPath $source.source_absolute -Destination $copiedPath
        $copiedHash = (Get-FileHash -LiteralPath $copiedPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($copiedHash -ne $source.sha256) { throw "Copy integrity failure: $fileRelative" }
        $row = [ordered]@{
            topic_slug = $topic.slug; topic_name_vi = $topic.name_vi; asset_id = $assetId
            subject = $source.subject; file_relative = $fileRelative; sha256 = $source.sha256
            bytes = $source.bytes; width = $source.png.width; height = $source.png.height
            alpha_channel_present = $source.png.alpha_channel_present
            transparency_chunk_present = $source.png.transparency_chunk_present
            shared_topic_slugs = ($source.topic_slugs -join '|')
            source_relative = $source.source_relative; source_absolute = $source.source_absolute
            style_reference = $plan.style_reference
        }
        $rows.Add([pscustomobject]$row)
        $imageUrl = [Uri]::EscapeDataString([string]$topic.slug) + '/' + [Uri]::EscapeDataString("$assetId.png")
        [void]$cards.AppendLine('<figure class="sticker" data-search="' + (Html ($assetId + ' ' + $source.subject)) + '"><a class="preview" href="' + $imageUrl + '" target="_blank" rel="noopener"><img loading="lazy" src="' + $imageUrl + '" alt="' + (Html $source.subject) + '"></a><figcaption><strong>' + (Html $assetId) + '</strong><span>' + (Html $source.subject) + '</span>' + $(if ($source.topic_slugs.Count -gt 1) { '<small>Dùng chung: ' + (Html ($source.topic_slugs -join ', ')) + '</small>' } else { '' }) + '</figcaption></figure>')
    }
    [void]$cards.AppendLine('</div></section>')
}
$rows | Export-Csv -LiteralPath (Join-Path $stagingPath 'sticker-mapping.csv') -NoTypeInformation -Encoding utf8BOM
$manifest = [ordered]@{
    schema_version = '1.0'; generated_utc = [DateTime]::UtcNow.ToString('o'); complete = $true
    topics = $plan.topics; shared_assets = $plan.shared_assets; assets = @($inventory)
    topic_files = @($rows); total_topic_files = $rows.Count; unique_source_pngs = $inventory.Count
    plan = $plan; png_processing = 'Byte-for-byte copies only. No image resizing or editing.'
    visual_qa_note = 'Packaging validates files and mappings, not subjective style or visible transparency.'
}
Write-JsonFile $manifest (Join-Path $stagingPath 'sticker-mapping.json')
Copy-Item -LiteralPath $planFile -Destination (Join-Path $metadataPath 'sticker-plan.json')
Copy-Item -LiteralPath $validationPath -Destination (Join-Path $metadataPath 'packaging-validation.json')
foreach ($noteFile in Get-ChildItem -LiteralPath $productionPath -File | Where-Object { $_.Extension -in @('.md', '.txt') }) {
    Copy-Item -LiteralPath $noteFile.FullName -Destination (Join-Path $metadataPath $noteFile.Name)
}
foreach ($notesDir in @('prompts', 'notes')) {
    $notesSource = Join-Path $productionPath $notesDir
    if (Test-Path -LiteralPath $notesSource -PathType Container) {
        Copy-Item -LiteralPath $notesSource -Destination (Join-Path $metadataPath $notesDir) -Recurse
    }
}
$htmlTemplate = @'
<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bộ sticker · 50 chủ đề</title>
<style>
:root{font-family:system-ui,sans-serif;color:#39342f;background:#f3efe8;--preview:#fff;--checker:rgba(0,0,0,.055)}
*{box-sizing:border-box}body{margin:0}header{padding:26px max(20px,4vw);background:#fffcf7;border-bottom:1px solid #ded6cc;position:sticky;top:0;z-index:5}h1{font-size:24px;margin:0 0 10px}header p{margin:6px 0 16px;color:#716659}.controls{display:flex;gap:9px;flex-wrap:wrap;align-items:center}input{width:min(470px,100%);padding:11px 14px;border:1px solid #c8bfb2;border-radius:8px;font:inherit}button{border:1px solid #b8ad9d;background:#fff;padding:10px 14px;border-radius:8px;font:inherit;cursor:pointer}button[aria-pressed=true]{background:#514c45;color:#fff}.count{margin-left:auto;color:#716659}main{padding:20px max(20px,4vw) 70px}.topic{margin-bottom:42px}h2{font-size:23px;margin:12px 0 0}.topic-slug{margin:4px 0 15px;color:#827367;font-size:13px}.stickers{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.sticker{margin:0;border:1px solid #dfd6ca;background:#fffdfa;border-radius:12px;overflow:hidden}.preview{display:flex;align-items:center;justify-content:center;height:220px;padding:17px;background-color:var(--preview);background-image:linear-gradient(45deg,var(--checker) 25%,transparent 25%),linear-gradient(-45deg,var(--checker) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--checker) 75%),linear-gradient(-45deg,transparent 75%,var(--checker) 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}.preview img{max-width:100%;max-height:100%;object-fit:contain}figcaption{padding:11px 13px;font-size:12px;min-height:84px}figcaption strong{display:block;font-size:13px;overflow-wrap:anywhere}figcaption span{display:block;margin-top:5px;color:#73685d}figcaption small{display:block;margin-top:7px;color:#927038}body.dark-preview{--preview:#343b43;--checker:rgba(255,255,255,.04)}[hidden]{display:none!important}.empty{padding:40px 0;color:#73685d}footer{font-size:12px;color:#827367;margin-top:35px}a{color:inherit}@media(min-width:1550px){.stickers{grid-template-columns:repeat(8,minmax(0,1fr))}.preview{height:175px}}@media(max-width:850px){.stickers{grid-template-columns:repeat(2,minmax(0,1fr))}.preview{height:190px}header{position:relative}.count{width:100%;margin:4px 0}}@media(max-width:420px){.preview{height:150px}}
</style></head><body>
<header><h1>Bộ sticker · 50 chủ đề</h1><p>__SLOT_COUNT__ sticker theo chủ đề · __UNIQUE_COUNT__ ảnh gốc · Bấm ảnh để mở PNG đầy đủ.</p><div class="controls"><input id="search" type="search" placeholder="Tìm chủ đề hoặc sticker…" aria-label="Tìm chủ đề hoặc sticker"><button id="light" type="button" aria-pressed="true">Nền sáng</button><button id="dark" type="button" aria-pressed="false">Nền tối</button><span class="count" id="count" aria-live="polite"></span></div></header>
<main>__TOPIC_CARDS__<p class="empty" id="empty" hidden>Không tìm thấy sticker phù hợp.</p><footer>PNG được sao chép nguyên bản. Nguồn và SHA-256 nằm trong <a href="sticker-mapping.json">sticker-mapping.json</a> và <a href="sticker-mapping.csv">sticker-mapping.csv</a>. Ghi chú phong cách và prompt nằm trong thư mục metadata.</footer></main>
<script>
const normalize = value => value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d');
const search = document.getElementById('search');
const sections = [...document.querySelectorAll('.topic')];
function filter(){const query=normalize(search.value.trim());let topics=0,stickers=0;for(const section of sections){const topicMatch=normalize(section.dataset.search).includes(query);let visible=0;for(const sticker of section.querySelectorAll('.sticker')){const match=topicMatch||normalize(sticker.dataset.search).includes(query);sticker.hidden=!match;if(match)visible++;}section.hidden=visible===0;if(visible){topics++;stickers+=visible;}}document.getElementById('count').textContent=topics+' chủ đề · '+stickers+' sticker';document.getElementById('empty').hidden=topics!==0;}
search.addEventListener('input',filter);filter();
for(const mode of ['light','dark'])document.getElementById(mode).addEventListener('click',()=>{document.body.classList.toggle('dark-preview',mode==='dark');for(const other of ['light','dark'])document.getElementById(other).setAttribute('aria-pressed',String(mode===other));});
</script></body></html>
'@
$html = $htmlTemplate.Replace('__SLOT_COUNT__', [string]$rows.Count).Replace('__UNIQUE_COUNT__', [string]$inventory.Count).Replace('__TOPIC_CARDS__', $cards.ToString())
$html | Set-Content -LiteralPath (Join-Path $stagingPath 'index.html') -Encoding utf8
@"
BỘ STICKER — 50 CHỦ ĐỀ

Mở index.html để xem và tìm kiếm; chuyển nền sáng/tối để kiểm tra PNG.
$($rows.Count) file theo chủ đề, từ $($inventory.Count) PNG gốc duy nhất.
Sticker dùng chung được sao chép nguyên bản vào đúng hai chủ đề.
sticker-mapping.csv / sticker-mapping.json ghi nguồn, SHA-256 và kích thước.
metadata/ lưu nguyên kế hoạch, ghi chú mỹ thuật và prompt hiện có.

Quá trình đóng gói chỉ sao chép dữ liệu; không chỉnh sửa hoặc resize ảnh.
Các kiểm tra file không thay thế đánh giá mỹ thuật trực quan.
"@ | Set-Content -LiteralPath (Join-Path $stagingPath 'README.txt') -Encoding utf8

# Before moving a directory on Windows, verify both absolute paths are in the intended workspace root.
$resolvedStagingPath = (Resolve-Path -LiteralPath $stagingPath).Path
if (-not $resolvedStagingPath.StartsWith($productionPrefix, [StringComparison]::OrdinalIgnoreCase) -or
    -not $deliveryPath.StartsWith($productionPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Resolved staging/delivery path escaped ProductionRoot; move refused.'
}
Move-Item -LiteralPath $resolvedStagingPath -Destination $deliveryPath
Write-Output "Packaged $($rows.Count) topic PNGs from $($inventory.Count) unique sources: $deliveryPath"
Write-Output "Catalogue: $(Join-Path $deliveryPath 'index.html')"
