#!/bin/bash
#
# move_complete_skus.sh
#
# Scans every SKU folder inside:
#   Mangalsutra/scale-image-only/
#
# If a SKU folder contains 4 or more image files (png/jpg/jpeg/webp),
# the entire SKU folder is MOVED into the main Mangalsutra/ folder.
# Incomplete SKU folders are left untouched inside scale-image-only/.
#
# Usage:
#   bash move_complete_skus.sh
#

set -euo pipefail

# ---------- CONFIG ----------
SCALE_DIR="/Volumes/ORICO/Svadezi Luxe product listing/EXCEL_SKUS/Mangalsutra/scale-image-only"
DEST_DIR="/Volumes/ORICO/Svadezi Luxe product listing/EXCEL_SKUS/Mangalsutra"
MIN_VARIANTS=4
# ----------------------------

if [[ ! -d "$SCALE_DIR" ]]; then
  echo "ERROR: scale-image-only folder not found:"
  echo "  $SCALE_DIR"
  exit 1
fi

copied=()
skipped=()

shopt -s nullglob

for sku_path in "$SCALE_DIR"/*/; do
  sku_name="$(basename "$sku_path")"

  # Count image files only
  count=$(find "$sku_path" -maxdepth 1 -type f \
    \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) \
    | wc -l | tr -d ' ')

  if (( count >= MIN_VARIANTS )); then
    if [[ -d "$DEST_DIR/$sku_name" ]]; then
      skipped+=("$sku_name ($count images) — already exists in Mangalsutra/, skipped")
    else
      mv "${sku_path%/}" "$DEST_DIR/"
      copied+=("$sku_name ($count images)")
    fi
  else
    skipped+=("$sku_name ($count images) — only $count image(s), needs $MIN_VARIANTS")
  fi
done

echo
echo "============================================="
echo "  SVADEZI — SCALE-IMAGE-ONLY SORT REPORT"
echo "============================================="
echo
echo "COPIED to Mangalsutra/ (>= $MIN_VARIANTS images):"
echo "---------------------------------------------"
if (( ${#copied[@]} == 0 )); then
  echo "  (none)"
else
  for s in "${copied[@]}"; do echo "  OK  $s"; done
fi
echo
echo "LEFT in scale-image-only/ (incomplete):"
echo "---------------------------------------------"
if (( ${#skipped[@]} == 0 )); then
  echo "  (none)"
else
  for s in "${skipped[@]}"; do echo "  --  $s"; done
fi
echo
echo "Total copied:  ${#copied[@]}"
echo "Total skipped: ${#skipped[@]}"
echo
echo "Destination: $DEST_DIR"
echo "============================================="
