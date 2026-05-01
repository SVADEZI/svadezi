#!/bin/bash
#
# move_complete_skus.sh
#
# Scans EVERY SKU folder in two places:
#   1. Top-level SKU folders inside Mangalsutra/
#   2. SKU folders inside Mangalsutra/scale-image-only/
#
# If a SKU folder has 4 or more image files (jpg/jpeg/png/webp),
# it is COPIED to the destination "main" mangalsutra folder.
# SKUs with fewer than 4 images are left untouched.
#
# Usage:
#   bash move_complete_skus.sh
#
# Edit BASE_DIR, DEST_DIR, and MIN_VARIANTS below if needed.
#

set -euo pipefail

# ---------- CONFIG ----------
BASE_DIR="/Volumes/ORICO/Svadezi Luxe product listing/EXCEL_SKUS/Mangalsutra"
DEST_DIR="/Volumes/ORICO/Svadezi Luxe product listing/Mangalsutra-MAIN"
MIN_VARIANTS=4
# ----------------------------

# Top-level helper folders that are NOT SKU folders (skip these when scanning top-level)
SKIP_AT_TOP=("no-scale-image" "scale-image-only" "pendants")

# Sources to scan: the top-level folder + the scale-image-only sub-folder
SCAN_DIRS=(
  "$BASE_DIR"
  "$BASE_DIR/scale-image-only"
)

if [[ ! -d "$BASE_DIR" ]]; then
  echo "ERROR: Base folder does not exist:"
  echo "  $BASE_DIR"
  exit 1
fi

mkdir -p "$DEST_DIR"

moved_skus=()
skipped_skus=()
duplicate_skus=()

shopt -s nullglob

scan_directory() {
  local dir="$1"
  local skip_helpers="$2"   # "yes" only for top-level scan

  if [[ ! -d "$dir" ]]; then
    return
  fi

  for sku_path in "$dir"/*/; do
    local sku_name
    sku_name="$(basename "$sku_path")"

    # On top-level scan, skip helper folders
    if [[ "$skip_helpers" == "yes" ]]; then
      local skip=false
      for s in "${SKIP_AT_TOP[@]}"; do
        if [[ "$sku_name" == "$s" ]]; then
          skip=true
          break
        fi
      done
      if $skip; then
        continue
      fi
    fi

    # Count image files (jpg/jpeg/png/webp), case-insensitive
    local count
    count=$(find "$sku_path" -maxdepth 1 -type f \
      \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) \
      | wc -l | tr -d ' ')

    local source_label
    if [[ "$skip_helpers" == "yes" ]]; then
      source_label="top-level"
    else
      source_label="scale-image-only"
    fi

    if (( count >= MIN_VARIANTS )); then
      # If destination already has this SKU, warn instead of overwriting
      if [[ -d "$DEST_DIR/$sku_name" ]]; then
        duplicate_skus+=("$sku_name (from $source_label, $count images) — already exists in destination, skipped")
      else
        cp -R "$sku_path" "$DEST_DIR/"
        moved_skus+=("$sku_name [$source_label] ($count images)")
      fi
    else
      skipped_skus+=("$sku_name [$source_label] ($count images)")
    fi
  done
}

# Scan top-level (skipping helper folders)
scan_directory "${SCAN_DIRS[0]}" "yes"

# Scan inside scale-image-only/ (no helpers to skip)
scan_directory "${SCAN_DIRS[1]}" "no"

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

if (( ${#duplicate_skus[@]} > 0 )); then
  echo
  echo "DUPLICATES (already in destination, not overwritten):"
  echo "---------------------------------------------"
  for s in "${duplicate_skus[@]}"; do echo "  !!  $s"; done
fi

echo
echo "Total copied:    ${#moved_skus[@]}"
echo "Total skipped:   ${#skipped_skus[@]}"
echo "Total duplicate: ${#duplicate_skus[@]}"
echo
echo "Destination: $DEST_DIR"
echo "============================================="
