# Journey Visual: Corpus Image Reuse

## Journey Overview

```
[Trigger: corpus add]   [Step 2: Browse]   [Step 3: Search]   [Step 4: Assess]   [Step 5: Adapt]   [Step 6: Insert]
   Extract images   -->  View catalog  -->  Find figures  -->  Evaluate fit -->  Update text  -->  Place in proposal
   from past work        of images          for current        for current        for new           with formatting
                                            proposal           context            solicitation

Feels: Anticipation     Feels: Organized    Feels: Hopeful    Feels: Confident  Feels: In control  Feels: Satisfied
Artifact: image-        Artifact: search    Artifact: match   Artifact: quality Artifact: adapted  Artifact: figure
  registry entries        results             candidates        assessment        caption/refs       in proposal
```

## Emotional Arc

**Pattern**: Confidence Building
- **Start**: Anticipation/Curiosity -- "Let me see what images I already have"
- **Middle**: Focused/Engaged -- "This diagram from my Navy win looks perfect for this section"
- **End**: Confident/Satisfied -- "Reused a proven figure, saved 2 hours, and it looks right"

**Peak tension**: Step 4 (Assess) -- the user evaluates whether a surfaced image is actually fit for the new proposal. Quality warnings, staleness flags, and compliance notes converge here.

**Resolution**: Step 5 (Adapt) -- once the user decides to proceed, the system helps them update textual elements, creating relief that nothing will slip through.

---

## Step 1: Image Extraction During Corpus Ingestion

**Command**: `corpus add ~/proposals/2024-Q1/`

**What changes**: The existing `corpus add` command gains image extraction as a side effect. When ingesting a PDF or DOCX, the system now also extracts embedded images, classifies them, and stores them with metadata.

### TUI Mockup

```
$ /sbir:proposal corpus add ~/proposals/2024-Q1/

Scanning ~/proposals/2024-Q1/ ...

  Documents:
    12 new documents ingested (4 pdfs, 5 mds, 3 docx)
    2 duplicates skipped

  Images extracted:
    23 images found across 7 documents
    ├── 8 system diagrams
    ├── 4 TRL roadmaps
    ├── 3 org charts
    ├── 3 concept illustrations
    ├── 2 market landscape figures
    ├── 2 charts (bar/line)
    └── 1 unclassified

    Quality:   19 high (>= 300 DPI)  |  3 medium (150-299 DPI)  |  1 low (< 150 DPI)
    Sources:   AF243-001 (WIN, 8 images)  |  N244-012 (LOSS, 6 images)  |  DARPA-HR-22 (WIN, 9 images)

  Image catalog: .sbir/corpus/images/
  Metadata:      .sbir/corpus/image-registry.json
```

### Emotional State
- **Entry**: Anticipation -- "I wonder what figures are buried in these old proposals"
- **Exit**: Pleased/Organized -- "23 images found and classified automatically"

---

## Step 2: Browse Image Catalog

**Command**: `corpus images list [--type <type>] [--source <proposal-id>] [--outcome <win|loss>]`

### TUI Mockup

```
$ /sbir:proposal corpus images list --type system-diagram --outcome win

  Image Catalog: system diagrams from winning proposals

  #    Source          Agency   Caption                              Quality  Page
  ───  ──────────────  ───────  ─────────────────────────────────── ────────  ────
  1    AF243-001       USAF     Fig 3: CDES System Architecture      high     7
  2    AF243-001       USAF     Fig 5: Phased Array Block Diagram    high     12
  3    DARPA-HR-22     DARPA    Fig 2: Multi-Agent Architecture      high     5
  4    DARPA-HR-22     DARPA    Fig 6: Deployment Architecture       medium   15

  4 images found. Filter: type=system-diagram, outcome=win

  Tip: Use 'corpus images show <#>' to view details and metadata.
```

### Emotional State
- **Entry**: Curious -- "What system diagrams do I have from wins?"
- **Exit**: Organized/Empowered -- "I can see exactly what is available, filtered by what matters"

---

## Step 3: Search for Relevant Images During Drafting

**Command**: `corpus images search "<query>" [--type <type>] [--agency <agency>] [--limit <n>]`

This is the writer/formatter integration point. When the writer or formatter needs a figure, they can search the corpus image index.

### TUI Mockup

```
$ /sbir:proposal corpus images search "directed energy system architecture" --agency USAF

  Searching image catalog for: "directed energy system architecture"

  Matches (ranked by relevance):

  #  Score  Source        Type              Caption                            Outcome  Age
  ── ─────  ────────────  ────────────────  ─────────────────────────────────  ───────  ────
  1  0.92   AF243-001     system-diagram    Fig 3: CDES System Architecture    WIN      8mo
  2  0.71   AF243-001     block-diagram     Fig 5: Phased Array Block Diagram  WIN      8mo
  3  0.45   DARPA-HR-22   system-diagram    Fig 2: Multi-Agent Architecture    WIN      14mo

  Use 'corpus images show <#>' for full details.
  Use 'corpus images use <#>' to select for current proposal.
```

### Emotional State
- **Entry**: Hopeful -- "I bet I have something from that Air Force win"
- **Exit**: Excited/Focused -- "Score 0.92, that's exactly what I need"

---

## Step 4: Assess Image Fitness

**Command**: `corpus images show <image-id>`

This is the critical trust-building step. The user evaluates whether a surfaced image is fit for the current proposal.

### TUI Mockup

```
$ /sbir:proposal corpus images show 1

  Image Details: AF243-001 / Figure 3

  ┌─ Source ──────────────────────────────────────────────┐
  │  Proposal:   AF243-001 (Compact Directed Energy)      │
  │  Agency:     USAF / AFRL                               │
  │  Outcome:    WIN                                       │
  │  Extracted:  2024-06-15                                │
  │  Page:       7 of 25                                   │
  │  Section:    Technical Approach                         │
  └────────────────────────────────────────────────────────┘

  ┌─ Image ───────────────────────────────────────────────┐
  │  File:       .sbir/corpus/images/af243-001-fig-03.png  │
  │  Type:       system-diagram                            │
  │  Resolution: 2048x1536 (300 DPI)                       │
  │  Quality:    HIGH                                      │
  │  Size:       847 KB                                    │
  └────────────────────────────────────────────────────────┘

  ┌─ Context ─────────────────────────────────────────────┐
  │  Caption:    "Figure 3: CDES System Architecture       │
  │              showing phased array subsystem,            │
  │              beam control unit, and power management"   │
  │                                                        │
  │  Surround:   "The proposed system architecture          │
  │              leverages our proven CDES platform..."     │
  └────────────────────────────────────────────────────────┘

  ┌─ Fitness Assessment ──────────────────────────────────┐
  │  Quality:       PASS (300 DPI, high resolution)        │
  │  Freshness:     OK (8 months old)                      │
  │  Agency match:  YES (same agency: USAF)                │
  │  Domain match:  HIGH (directed energy, system arch)    │
  │                                                        │
  │  Warnings:                                             │
  │   [!] Caption references "CDES" -- verify system name  │
  │       matches current proposal                         │
  │   [!] Labels may contain proposal-specific text --     │
  │       manual review recommended before insertion       │
  └────────────────────────────────────────────────────────┘

  ┌─ Attribution ─────────────────────────────────────────┐
  │  Origin:     Company-created (not gov-furnished)       │
  │  Reuse:      No restrictions identified                │
  └────────────────────────────────────────────────────────┘

  Actions:
    corpus images use 1        Select for current proposal
    corpus images skip 1       Mark as not relevant
    corpus images flag 1       Flag for compliance review
```

### Emotional State
- **Entry**: Evaluative/Careful -- "Is this actually usable?"
- **Exit**: Confident -- "High quality, same agency, win, and it flagged the label I need to check"

---

## Step 5: Adapt Reused Image

**Command**: `corpus images use <image-id> --section <section> --figure-number <n>`

When the user selects an image for reuse, the system generates an adapted caption, figure reference, and flags elements that need manual editing in the image itself.

### TUI Mockup

```
$ /sbir:proposal corpus images use 1 --section technical-approach --figure-number 3

  Preparing image for reuse in current proposal...

  ┌─ Adapted Figure ──────────────────────────────────────┐
  │  Figure number:  Figure 3                              │
  │  Section:        Technical Approach                     │
  │  File copied to: ./artifacts/wave-5-visuals/figure-3-  │
  │                  system-architecture.png                │
  └────────────────────────────────────────────────────────┘

  ┌─ Caption (adapted) ──────────────────────────────────-┐
  │  Original: "Figure 3: CDES System Architecture         │
  │            showing phased array subsystem, beam         │
  │            control unit, and power management"          │
  │                                                        │
  │  Proposed: "Figure 3: System Architecture showing       │
  │            phased array subsystem, beam control unit,   │
  │            and power management"                        │
  │                                                        │
  │  [!] Removed "CDES" -- verify replacement system name  │
  └────────────────────────────────────────────────────────┘

  ┌─ Manual Review Needed ────────────────────────────────┐
  │  The image file itself may contain embedded text:       │
  │   - System name labels in the diagram                  │
  │   - Component names referencing AF243-001 context      │
  │                                                        │
  │  Open the image in an editor to verify and update      │
  │  labels before proceeding to formatting.               │
  └────────────────────────────────────────────────────────┘

  ┌─ Tracking ────────────────────────────────────────────┐
  │  Source:       AF243-001, Figure 3                     │
  │  Method:       corpus-reuse                            │
  │  Attribution:  Recorded in figure-log.md               │
  │  Review:       pending-manual-review                   │
  └────────────────────────────────────────────────────────┘

  Next: Edit image labels if needed, then approve via formatter.
```

### Emotional State
- **Entry**: Decisive -- "I am going with this one"
- **Exit**: In control -- "Caption adapted, warnings clear, I know exactly what to check"

---

## Step 6: Integration with Formatter

When the formatter encounters a figure with `method: corpus-reuse` in the figure plan/inventory, it treats it as a pre-existing asset rather than generating a new one. The review checkpoint still applies.

### TUI Mockup (Formatter perspective)

```
  Figure 3: System Architecture

  ┌─ Generation ──────────────────────────────────────────┐
  │  Method:   corpus-reuse (from AF243-001)               │
  │  Status:   pending-manual-review                       │
  │  File:     ./artifacts/wave-5-visuals/figure-3-        │
  │            system-architecture.png                      │
  │  Quality:  300 DPI, 2048x1536                          │
  └────────────────────────────────────────────────────────┘

  Review this figure:
    [approve]  Image labels verified, ready for insertion
    [revise]   Need to update image labels first
    [replace]  Replace with a newly generated figure instead

  Caption: "Figure 3: System Architecture showing phased
           array subsystem, beam control unit, and power
           management"
```

### Emotional State
- **Entry**: Checking -- "Let me verify this looks right in context"
- **Exit**: Satisfied -- "Reused a proven figure, saved hours, everything cross-references correctly"

---

## Error Paths

### E1: No Images Found in Corpus Documents

```
$ /sbir:proposal corpus add ~/proposals/text-only/

  Documents: 5 new documents ingested (3 pdfs, 2 docx)
  Images extracted: 0 images found

  Note: No embedded images detected. Documents may be text-only
  or images may not be extractable from this file format.
```

### E2: Low Quality Image Surfaced

```
  Fitness Assessment:
    Quality:    FAIL (72 DPI -- below 300 DPI minimum for submission)
    Resolution: 640x480 (insufficient for print)

    This image is too low-resolution for proposal submission.
    Consider: generating a new figure based on this design.
```

### E3: Government-Furnished Image Detected

```
  Attribution:
    Origin:   UNKNOWN -- source cannot be confirmed as company-created
    Warning:  This image may be government-furnished material.
              Do not reuse without explicit permission from the
              contracting officer.

    Action:   corpus images flag 7 --reason "possible-gov-furnished"
```

### E4: Image Extraction Failure

```
  Images extracted:
    18 images found across 6 documents
    2 images failed extraction (corrupted or unsupported encoding)
    ├── AF243-001.pdf page 14: extraction failed (JBIG2 encoding)
    └── N244-012.docx image 3: extraction failed (WMF format)

    Tip: Open these documents manually to extract the images.
```

### E5: Stale Image with Outdated Content

```
  Fitness Assessment:
    Freshness:  WARNING (26 months old)
    [!] This image is from a proposal over 2 years old.
        Team members, org structure, or technical approach
        may have changed significantly.
        Manual review strongly recommended.
```
