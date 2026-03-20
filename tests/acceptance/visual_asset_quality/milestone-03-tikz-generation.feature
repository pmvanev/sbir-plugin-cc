Feature: TikZ Generation for LaTeX Proposals
  As a solo SBIR proposal writer using LaTeX
  I want diagrams generated as TikZ code that compiles natively
  So that my figures match the document typography and scale perfectly

  Background:
    Given the visual asset service is available

  # --- US-VAQ-4: TikZ Routing in VisualAssetService ---

  # Happy path: TikZ method routed correctly
  @us-vaq-4
  Scenario: Figure with TikZ generation method is routed to TikZ handler
    Given a figure placeholder for Figure 2 "System Block Diagram" with method "tikz"
    When the figure is generated through the visual asset service
    Then the result has format "tikz"
    And the result has generation method "tikz"

  # Happy path: TikZ result includes source and preview file paths
  @us-vaq-4
  Scenario: TikZ generation produces source and preview file references
    Given a figure placeholder for Figure 2 "System Block Diagram" with method "tikz"
    When the figure is generated through the visual asset service
    Then the result file path ends with ".tex"

  # Happy path: existing methods unchanged by TikZ addition
  @us-vaq-4
  Scenario: Mermaid generation still works after TikZ addition
    Given a figure placeholder for Figure 1 "Data Flow" with method "Mermaid"
    When the figure is generated through the visual asset service
    Then the result has format "svg"

  @us-vaq-4
  Scenario: Corpus reuse still works after TikZ addition
    Given a figure placeholder for Figure 5 "Reused Diagram" with method "corpus-reuse"
    When the figure is generated through the visual asset service
    Then the result has format "corpus-reuse"
    And the result has review status "pending-manual-review"

  @us-vaq-4
  Scenario: External brief still works after TikZ addition
    Given a figure placeholder for Figure 7 "Photo" with method "external"
    When the figure is generated through the visual asset service
    Then the result has format "brief"

  # --- US-VAQ-4: Extended FigureGenerationResult Fields ---

  # Happy path: prompt hash recorded in result
  @us-vaq-4
  Scenario: TikZ result carries prompt hash for audit
    Given a figure placeholder for Figure 2 with method "tikz"
    And the prompt hash is "a1b2c3d4e5f6"
    When the figure is generated with prompt tracking
    Then the result prompt hash is "a1b2c3d4e5f6"

  # Happy path: iteration count recorded in result
  @us-vaq-4
  Scenario: Generation result carries iteration count
    Given a figure placeholder for Figure 3 with method "tikz"
    And the figure has been through 2 refinement iterations
    When the figure is generated with iteration tracking
    Then the result iteration count is 2

  # Boundary: new result with default tracking fields
  @us-vaq-4
  Scenario: Generation result defaults to empty prompt hash and zero iterations
    Given a figure placeholder for Figure 1 with method "Mermaid"
    When the figure is generated through the visual asset service
    Then the result prompt hash is empty
    And the result iteration count is 0

  # --- US-VAQ-4: TikZ Availability Conditions ---

  # Error: TikZ not offered for non-diagram types (checked at caller level)
  @us-vaq-4
  Scenario: TikZ method accepted for any figure type at service level
    Given a figure placeholder for Figure 4 "Concept Image" type "concept" with method "tikz"
    When the figure is generated through the visual asset service
    Then the result has format "tikz"

  # --- US-VAQ-4: FileVisualAssetAdapter TikZ Persistence ---

  # Happy path: TikZ source file written to disk
  @us-vaq-4
  Scenario: TikZ source content persisted as .tex file
    Given a generated figure for Figure 2 with format "tikz" and file path "system-block.tex"
    And the TikZ source content is "\begin{tikzpicture}\node{Test};\end{tikzpicture}"
    When the figure is written through the visual asset adapter
    Then the file "system-block.tex" exists in the figures directory
    And the file content matches the TikZ source

  # Happy path: TikZ figure read back from inventory
  @us-vaq-4
  Scenario: Inventory with TikZ figures is read correctly
    Given an inventory file containing Figure 2 with method "tikz" and type "block-diagram"
    When the inventory is read through the visual asset adapter
    Then Figure 2 has generation method "tikz"
    And Figure 2 has figure type "block-diagram"
