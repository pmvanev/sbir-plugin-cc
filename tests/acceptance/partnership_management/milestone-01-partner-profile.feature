Feature: Partner Profile Builder (US-PM-001)
  As an SBIR proposal writer with research institution partners
  I want to create and manage structured partner profiles
  So that all proposal agents can generate partnership-aware content

  Background:
    Given the partner profile validation service is available

  # --- Happy Path: Profile Creation and Retrieval ---

  Scenario: Valid partner profile passes schema validation
    Given Phil has prepared a complete partner profile for "SWRI" as a federally funded R&D center
    And the profile includes capabilities "intelligent systems, autonomy, sensor fusion, applied ML"
    And the profile includes key personnel "Dr. Rebecca Chen" as Co-PI with expertise "autonomous navigation, sensor fusion"
    And the profile includes facility "6-DOF motion sim lab"
    And the profile includes a past collaboration with "Navy" on "Autonomous UUV" with outcome "awarded"
    And the profile includes STTR eligibility as qualifying with minimum effort capable
    When Phil submits the partner profile for validation
    Then the partner profile passes validation with no errors

  Scenario: Partner profile preserves all six sections after save and reload
    Given Phil has prepared a complete partner profile for "CU Boulder" as a university
    And the profile includes 3 capabilities
    And the profile includes 2 key personnel entries
    And the profile includes 1 facility
    And the profile includes 1 past collaboration
    And the profile includes STTR eligibility as qualifying
    When the partner profile is validated and saved
    And the partner profile is reloaded from disk
    Then the reloaded profile has 3 capabilities
    And the reloaded profile has 2 key personnel entries
    And the reloaded profile has 1 facility
    And the reloaded profile has 1 past collaboration

  @skip
  Scenario: Combined capability analysis shows overlap and unique capabilities
    Given Phil has a company profile with capabilities "directed energy, RF engineering, machine learning"
    And Phil has a partner profile for "SWRI" with capabilities "intelligent systems, autonomy, sensor fusion, applied ML"
    When the combined capability analysis is computed
    Then the overlap includes "machine learning"
    And capabilities unique to Phil's company include "directed energy, RF engineering"
    And capabilities unique to SWRI include "intelligent systems, autonomy, sensor fusion"

  # --- Happy Path: Profile Update ---

  @skip
  Scenario: Updating partner profile preserves existing data
    Given a partner profile exists for "CU Boulder" with 2 key personnel entries
    When Phil adds a third key personnel entry for "Dr. James Rivera" with expertise "underwater robotics, acoustic sensing"
    And the updated profile is validated and saved
    Then the profile now has 3 key personnel entries
    And the existing 2 key personnel entries are preserved

  # --- Error Path: Validation Failures ---

  @skip
  Scenario: Empty capabilities array blocks save with actionable error
    Given Phil has prepared a partner profile with empty capabilities
    When Phil submits the partner profile for validation
    Then validation reports that capabilities must have at least 1 keyword
    And the partner profile is not saved

  @skip
  Scenario: Missing partner name blocks save
    Given Phil has prepared a partner profile with no partner name
    When Phil submits the partner profile for validation
    Then validation reports that partner name is required
    And the partner profile is not saved

  @skip
  Scenario: Invalid partner type blocks save
    Given Phil has prepared a partner profile with partner type "corporation"
    When Phil submits the partner profile for validation
    Then validation reports that partner type must be university, federally funded R&D center, or nonprofit research
    And the partner profile is not saved

  # --- Error Path: File Safety ---

  @skip
  Scenario: Cancel during profile creation writes no files
    Given Phil is creating a partner profile for "NDSU"
    When Phil cancels the profile creation
    Then no partner profile file exists for "NDSU"
    And the partners directory is unchanged

  @skip
  Scenario: Existing profile triggers overwrite protection
    Given a partner profile already exists for "CU Boulder"
    When Phil attempts to create a new profile for "CU Boulder"
    Then the tool detects the existing profile
    And the existing profile is not overwritten without explicit confirmation

  # --- Boundary: Schema Constraints ---

  @skip
  Scenario: Partner slug is deterministic from partner name
    Given Phil creates a partner profile for "Southwest Research Institute"
    When the partner slug is computed
    Then the slug is "southwest-research-institute"
    And creating a profile with the same name produces the same slug

  @skip
  Scenario: Key personnel entry requires name and at least one expertise keyword
    Given Phil has prepared a partner profile with a key personnel entry missing expertise
    When Phil submits the partner profile for validation
    Then validation reports that each key personnel entry requires at least one expertise keyword

  @property @skip
  Scenario: Valid partner profile always passes schema validation after round-trip
    Given any valid partner profile with all required fields populated
    When the profile is saved and reloaded
    Then the reloaded profile passes schema validation
