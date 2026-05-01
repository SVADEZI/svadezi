#!/bin/bash
#
# move_complete_skus.sh
#
# Scans every SKU folder inside the source Mangalsutra folder.
# If a SKU folder has 4 or more image files (jpg/jpeg/png/webp),
# it is COPIED to the destination "main" mangalsutra folder.
# SKUs with fewer than 4 images are left untouched.
#
# Usage:
#   ./move_complete_skus.sh
#
# Edit SOURCE_DIR, DEST_DIR, and MIN_VARIANTS below if needed.
#

set -euo pipefail

# ---------- CONFIG ----------
SOURCE_DIR="/Volumes/ORICO/Svadezi Luxe product listing/EXCEL_SKUS/Mangalsutra"
DEST_DIR="/Volumes/ORICO/Svadezi Luxe product listing/Mangalsutra-MAIN"
MIN_VARIANTS=4
# ----------------------------

# Folders inside SOURCE_DIR that are NOT SKU folders (skip these)
SKIP_FOLDERS=("no-scale-image" "scale-image-only" "pendants")

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "ERROR: Source folder does not exist:"
  echo "  $SOURCE_DIR"
  exit 1
fi

mkdir -p "$DEST_DIR"

moved_skus=()
skipped_skus=()

shopt -s nullglob

for sku_path in "$SOURCE_DIR"/*/; do
  sku_name="$(basename "$sku_path")"

  # Skip non-SKU helper folders
  skip=false
  for s in "${SKIP_FOLDERS[@]}"; do
    if [[ "$sku_name" == "$s" ]]; then
      skip=true
      break
    fi
  done
  if $skip; then
    continue
  fi

  # Count image files (jpg/jpeg/png/webp), case-insensitive
  count=$(find "$sku_path" -maxdepth 1 -type f \
    \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) \
    | wc -l | tr -d ' ')

  if (( count >= MIN_VARIANTS )); then
    cp -R "$sku_path" "$DEST_DIR/"
    moved_skus+=("$sku_name ($count images)")
  else
    skipped_skus+=("$sku_name ($count images)")
  fi
done

echo
echo "============================================="
echo "  SVADEZI MANGALSUTRA — SKU SORT REPORT"
echo "============================================="
echo
echo "COPIED to main folder (>= $MIN_VARIANTS variants):"
echo "---------------------------------------------"
if (( ${#moved_skus[@]} == 0 )); then
  echo "  (none)"
else
  for s in "${moved_skus[@]}"; do echo "  OK  $s"; done
fi
echo
echo "LEFT in place (< $MIN_VARIANTS variants):"
echo "---------------------------------------------"
if (( ${#skipped_skus[@]} == 0 )); then
  echo "  (none)"
else
  for s in "${skipped_skus[@]}"; do echo "  --  $s"; done
fi
echo
echo "Total copied:  ${#moved_skus[@]}"
echo "Total skipped: ${#skipped_skus[@]}"
echo
echo "Destination: $DEST_DIR"
echo "============================================="
