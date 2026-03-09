#!/usr/bin/env bash
# nano-banana-generate.sh — Generate images via Google Gemini Nano Banana API
#
# Usage:
#   scripts/nano-banana-generate.sh \
#     --prompt "Description of the image to generate" \
#     --output ./artifacts/wave-5-visuals/figure-name.png \
#     [--aspect-ratio 16:9] \
#     [--size 2K] \
#     [--model gemini-3.1-flash-image-preview]
#
# Requires:
#   GEMINI_API_KEY environment variable
#   curl, python3 (for base64 decoding)
#
# Exit codes:
#   0 — success, image written to output path
#   1 — missing dependencies or configuration
#   2 — API error

set -euo pipefail

# Defaults
ASPECT_RATIO="16:9"
IMAGE_SIZE="2K"
MODEL="gemini-3.1-flash-image-preview"
PROMPT=""
OUTPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --aspect-ratio)
            ASPECT_RATIO="$2"
            shift 2
            ;;
        --size)
            IMAGE_SIZE="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# Validate required inputs
if [[ -z "$PROMPT" ]]; then
    echo "Error: --prompt is required" >&2
    exit 1
fi

if [[ -z "$OUTPUT" ]]; then
    echo "Error: --output is required" >&2
    exit 1
fi

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
    echo "Error: GEMINI_API_KEY environment variable is not set" >&2
    echo "Get an API key at https://ai.google.dev/" >&2
    exit 1
fi

# Check dependencies
for cmd in curl python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: $cmd is required but not found" >&2
        exit 1
    fi
done

# Ensure output directory exists
OUTPUT_DIR="$(dirname "$OUTPUT")"
mkdir -p "$OUTPUT_DIR"

# Build request payload
PAYLOAD=$(python3 -c "
import json
payload = {
    'contents': [{
        'parts': [{'text': '''$PROMPT'''}]
    }],
    'generationConfig': {
        'responseModalities': ['TEXT', 'IMAGE'],
        'imageConfig': {
            'aspectRatio': '$ASPECT_RATIO',
            'imageSize': '$IMAGE_SIZE'
        }
    }
}
print(json.dumps(payload))
")

# Call Gemini API
API_URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent"

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${API_URL}" \
    -H "x-goog-api-key: ${GEMINI_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed '$d')
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -1)

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "Error: Gemini API returned HTTP $HTTP_CODE" >&2
    echo "$HTTP_BODY" | python3 -c "
import sys, json
try:
    resp = json.load(sys.stdin)
    if 'error' in resp:
        print(f\"  {resp['error'].get('message', 'Unknown error')}\", file=sys.stderr)
except:
    pass
" 2>&1 >&2
    exit 2
fi

# Extract base64 image data from response
python3 -c "
import json, base64, sys

response = json.loads('''$HTTP_BODY''')

# Find the image part in the response
for candidate in response.get('candidates', []):
    for part in candidate.get('content', {}).get('parts', []):
        if 'inlineData' in part:
            image_data = base64.b64decode(part['inlineData']['data'])
            with open('$OUTPUT', 'wb') as f:
                f.write(image_data)
            mime = part['inlineData'].get('mimeType', 'image/png')
            print(f'Image saved: $OUTPUT ({len(image_data)} bytes, {mime})')
            sys.exit(0)

print('Error: No image data found in API response', file=sys.stderr)
sys.exit(2)
"
