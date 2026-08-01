#!/bin/sh
# Build the folder to upload to Hostinger.
#
#   ./deploy/build.sh              -> dist/  (for the domain root)
#   ./deploy/build.sh jyotish      -> dist/  (for https://site.com/jyotish/)
#
# Upload the CONTENTS of dist/ into that folder on the server.
set -e
cd "$(dirname "$0")/.."
FOLDER="${1:-}"
OUT="dist"

rm -rf "$OUT"
mkdir -p "$OUT/engine"

# Regenerate the browser city table so place lookup works with no backend.
python3 -m jyotish.places >/dev/null 2>&1 || .venv/bin/python -m jyotish.places

# The static shell, served directly by Apache.
cp ui/index.html ui/cities.json ui/icon.svg ui/manifest.webmanifest "$OUT/"

# The Python engine, kept in a subfolder and blocked from direct download.
cp -R jyotish "$OUT/engine/"
mkdir -p "$OUT/engine/deploy" "$OUT/engine/ui"
cp deploy/index.cgi "$OUT/engine/deploy/"
cp requirements.txt "$OUT/engine/" 2>/dev/null || true
# router.py serves static files from ui/ as a fallback; give it the same copies.
cp ui/index.html ui/cities.json ui/icon.svg ui/manifest.webmanifest "$OUT/engine/ui/"

# Routing rules.
cp deploy/htaccess-for-app-folder "$OUT/.htaccess"
cp deploy/htaccess-for-engine-folder "$OUT/engine/.htaccess"

chmod 755 "$OUT/engine/deploy/index.cgi"
find "$OUT" -type d -exec chmod 755 {} \;
find "$OUT" -type f ! -name "index.cgi" -exec chmod 644 {} \;
chmod 755 "$OUT/engine/deploy/index.cgi"

echo "Built $OUT/"
echo
echo "  Upload the CONTENTS of $OUT/ to:"
if [ -n "$FOLDER" ]; then
  echo "    public_html/$FOLDER/"
  echo "  Then open:  https://your-domain.com/$FOLDER/"
  echo "  Check:      https://your-domain.com/$FOLDER/api/diag"
else
  echo "    public_html/"
  echo "  Then open:  https://your-domain.com/"
  echo "  Check:      https://your-domain.com/api/diag"
fi
echo
echo "  On the server, once, over SSH:"
echo "    pip3 install --user pyswisseph tzdata"
echo
echo "  index.cgi must be chmod 755. FTP clients often drop the bit."
