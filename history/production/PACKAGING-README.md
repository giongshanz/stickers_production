# Sticker packaging helper

`Pack-Stickers.ps1` reads `sticker-plan.json` and `unique/{asset-id}.png`. It does not generate, resize, edit, or overwrite artwork, and never writes to the desktop `NewStickers` folder.

From PowerShell 7:

```powershell
& ./Pack-Stickers.ps1 -ValidateOnly
& ./Pack-Stickers.ps1
```

Run final packaging only after all image generation and visual QA are complete. `-ValidateOnly` writes an honest inventory to `packaging-validation.json`; it returns exit code 2 while anything is missing or invalid. The default final destination is a new `delivery` directory beneath this production directory. An existing delivery is preserved: pass a different `-DeliveryRoot` beneath this directory to make another package. `-PlanPath` can select another plan filename.

The helper validates exactly 50 topics, at least 8 distinct assets per topic, safe and unique IDs/slugs, complete source files, shared assets matching exactly two topic usages, PNG structure and successful read-only decoding. It hashes each source and verifies every copied PNG byte-for-byte. Missing files prevent final packing; partially populated topics are never presented as complete. A failed copy may leave a `.delivery-staging-*` directory for inspection and does not claim a successful delivery.

The package contains 50 topic directories, a searchable `index.html` with light/dark image backgrounds, source/subject/topic/hash/dimension mappings in CSV and JSON, and a `metadata` folder preserving the full plan, validation report, top-level Markdown/text notes, and any `prompts` or `notes` directories. No original reference artwork is copied. Existing style-reference paths are preserved in the plan and mappings.

PNG alpha metadata reports whether an alpha channel or transparency chunk exists. It does not assert that any pixels are transparent. Visual style, anatomy, small-scale readability, actual transparency, and topic fit still require visual QA. Duplicate image bytes under different source IDs and missing alpha storage are surfaced as warnings.
