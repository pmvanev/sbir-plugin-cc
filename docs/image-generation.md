# Image Generation Setup (Optional)

The plugin can generate concept figures using Google's Gemini API during Wave 5. Without it, the formatter produces structural diagrams (SVG, Mermaid, Graphviz) and writes specification briefs for figures you create manually.

1. Get an API key at [Google AI Studio](https://ai.google.dev/) (free tier: 500 images/day)
2. Add to your shell profile:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
3. Restart your terminal. The formatter agent detects the key automatically during Wave 5.
