Feature: Visual Asset Quality Integration Checkpoints
  As a solo SBIR proposal writer
  I want all visual asset components to work together correctly
  So that style profiles feed into prompts and critique feeds into quality summaries

  Background:
    Given the visual asset service is available

  # --- Checkpoint 1: Style-to-Prompt Consistency ---

  @integration @checkpoint-1
  Scenario: Style profile palette colors appear in all rendered prompts
    Given an approved style profile with palette primary "#003366" and secondary "#6B7B8D"
    And a prompt template for Figure 1 type "system-diagram"
    And a prompt template for Figure 3 type "concept"
    When both prompts are rendered with the style profile
    Then both rendered prompts contain "#003366" and "#6B7B8D"

  # --- Checkpoint 2: Critique-to-Quality Consistency ---

  @integration @checkpoint-2
  Scenario: Quality summary reflects actual critique ratings
    Given Figure 1 was critiqued with average rating 4.2
    And Figure 3 was critiqued with average rating 3.8
    When the quality summary is computed
    Then the summary shows Figure 1 with rating 4.2
    And the summary shows Figure 3 with rating 3.8
    And the overall average is 4.0

  # --- Checkpoint 3: TikZ Routing Preserves Tracking Fields ---

  @integration @checkpoint-3
  Scenario: TikZ generation result carries prompt hash through the pipeline
    Given a figure placeholder for Figure 2 with method "tikz"
    And a prompt hash "abc123" was computed before generation
    When the figure is generated and the result is approved
    Then the approved result retains prompt hash "abc123"

  # --- Checkpoint 4: Cross-Method Generation Consistency ---

  @integration @checkpoint-4
  Scenario: Mixed generation methods all produce valid results
    Given Figure 1 uses method "Mermaid"
    And Figure 2 uses method "tikz"
    And Figure 5 uses method "corpus-reuse"
    And Figure 7 uses method "external"
    When all figures are generated through the visual asset service
    Then all 4 results have valid format fields
    And all 4 results have valid review status fields

  # --- Checkpoint 5: File Persistence Across Formats ---

  @integration @checkpoint-5
  Scenario: Inventory with mixed generation methods persists and loads correctly
    Given an inventory with Figure 1 method "Mermaid", Figure 2 method "tikz", and Figure 3 method "external"
    When the inventory is written and read back through the adapter
    Then the loaded inventory has 3 figures
    And each figure retains its original generation method
