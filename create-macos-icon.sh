#!/bin/bash
# Script to create macOS .icns from PNG files
# Requires: iconutil (comes with macOS)

set -e

echo "Creating macOS icon (.icns) from PNG files..."

# Create iconset directory
ICONSET_DIR="favicon.iconset"
mkdir -p "$ICONSET_DIR"

# Source images (using existing favicons)
SOURCE_DIR="backend/static"

# Check if we have source images
if [ ! -f "$SOURCE_DIR/favicon-48px.png" ]; then
    echo "Error: favicon-48px.png not found in $SOURCE_DIR"
    exit 1
fi

# Copy and resize images to required sizes
# macOS requires these specific sizes:
# - 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
# - @2x versions for Retina displays

# Use sips (built-in macOS tool) to resize
echo "Generating icon sizes..."

# 16x16
sips -z 16 16 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_16x16.png" > /dev/null
sips -z 32 32 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_16x16@2x.png" > /dev/null

# 32x32
sips -z 32 32 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_32x32.png" > /dev/null
sips -z 64 64 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_32x32@2x.png" > /dev/null

# 64x64 (if source is large enough)
sips -z 64 64 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_64x64.png" > /dev/null
sips -z 128 128 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_64x64@2x.png" > /dev/null

# 128x128
sips -z 128 128 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_128x128.png" > /dev/null
sips -z 256 256 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null

# 256x256
sips -z 256 256 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_256x256.png" > /dev/null
sips -z 512 512 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null

# 512x512
sips -z 512 512 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_512x512.png" > /dev/null
sips -z 1024 1024 "$SOURCE_DIR/favicon-48px.png" --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null

echo "Converting to .icns..."
iconutil -c icns "$ICONSET_DIR" -o "$SOURCE_DIR/favicon.icns"

echo "Cleaning up..."
rm -rf "$ICONSET_DIR"

echo "✅ macOS icon created: $SOURCE_DIR/favicon.icns"
