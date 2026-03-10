Feature: Document Formatting and Volume Assembly (US-011)
  As an engineer with approved figures and drafted content
  I want formatting handled by template and volumes assembled automatically
  So I can stop spending hours on mechanical formatting work

  Background:
    Given the proposal plugin is active
    And Phil has an active proposal with all figures approved

  # --- Formatting: Happy Path ---

  Scenario: Apply solicitation formatting rules
    Given the solicitation requires Times New Roman 12pt and 1-inch margins
    When Phil formats the proposal selecting "Microsoft Word (.docx)"
    Then the tool applies font, margins, headers, footers, and section numbering
    And the output medium is recorded in the proposal state

  @skip
  Scenario: Insert figures and format references
    Given 5 approved figures exist and the document has 23 citations
    When the tool inserts figures and formats references
    Then each figure appears at its correct position with its approved caption
    And citations are formatted in a consistent style

  # --- Jargon Audit ---

  @skip
  Scenario: Jargon audit flags undefined acronyms
    Given the document uses 15 unique acronyms
    And 2 are not defined on first use
    When the tool runs the jargon audit
    Then it flags the 2 undefined acronyms with their locations
    And the audit is written to the formatting artifacts directory

  # --- Page Count ---

  @skip
  Scenario: Page count within solicitation limits
    Given the formatted technical volume is 19 pages
    And the solicitation limit is 20 pages
    When the tool reports the page count
    Then Phil sees "19/20 -- within limit (1 page margin)"

  @skip
  Scenario: Page count over limit with guidance
    Given the formatted technical volume is 22 pages against a 20-page limit
    When the tool reports the page count
    Then Phil sees "22/20 -- OVER LIMIT by 2 pages"
    And Phil sees the 3 largest sections with page counts
    And Phil sees trimming suggestions

  # --- Compliance Final Check ---

  @skip
  Scenario: Compliance matrix final check during formatting
    Given the compliance matrix has 47 items
    And 45 are covered and 2 are waived with reasons
    When the tool runs the final compliance check
    Then it reports "45/47 covered | 2 waived (with reasons) | 0 missing"
    And the final check is written to the formatting artifacts directory

  @skip
  Scenario: Compliance matrix check flags missing items
    Given the compliance matrix has 47 items
    And 1 item has status "missing" with no coverage and no waiver
    When the tool runs the final compliance check
    Then it reports the missing item with guidance to provide content or waive

  # --- Assembly ---

  @skip
  Scenario: Assemble volumes and present for review
    Given formatting and compliance checks are complete
    When the tool assembles volumes
    Then it creates Volume 1 (Technical), Volume 2 (Cost), and Volume 3 (Company Info)
    And the volumes are written to the assembly artifacts directory
    And a human checkpoint is presented for assembled package review
