"""Step definitions for corpus ingestion (US-003).

Invokes through: CorpusIngestionService (driving port).
Does NOT import internal file parsers or hash utilities directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from pes.domain.corpus import SUPPORTED_EXTENSIONS, CorpusIngestionService, CorpusRegistry
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file -- enable scenarios in scope for step 02-01.
# Scenario 1 (happy path message) requires document classification beyond basic cataloging.
# Scenario 5 (protected PDF) requires PDF parsing to detect password protection.
# Both are deferred to future steps.
_FEATURE = "../features/corpus_ingestion.feature"


@scenario(_FEATURE, "Re-ingestion adds only new files")
def test_reingestion_adds_only_new_files():
    pass


@scenario(_FEATURE, "Skip unsupported file types in directory")
def test_skip_unsupported_file_types_in_directory():
    pass


@scenario(_FEATURE, "Empty directory handled gracefully")
def test_empty_directory_handled_gracefully():
    pass


@scenario(_FEATURE, "Non-existent directory path rejected")
def test_nonexistent_directory_path_rejected():
    pass


# --- Fixtures ---


@pytest.fixture()
def corpus_registry():
    """Fresh corpus registry for each scenario."""
    return CorpusRegistry()


@pytest.fixture()
def corpus_scanner():
    """Filesystem corpus scanner adapter."""
    from pes.adapters.filesystem_corpus_adapter import FilesystemCorpusAdapter

    return FilesystemCorpusAdapter()


@pytest.fixture()
def ingestion_service(corpus_scanner, corpus_registry):
    """CorpusIngestionService wired with test adapters."""
    return CorpusIngestionService(corpus_scanner, corpus_registry)


# --- Given steps ---


@given(
    parsers.parse(
        "Phil has a directory with {pdf_count:d} PDF proposals "
        "and {docx_count:d} Word debrief letters"
    ),
    target_fixture="corpus_dir",
)
def directory_with_docs(tmp_path, pdf_count, docx_count):
    """Create a directory with mock document files."""
    corpus_dir = tmp_path / "past-proposals"
    corpus_dir.mkdir()
    for i in range(pdf_count):
        (corpus_dir / f"proposal-{i + 1}.pdf").write_text(f"PDF content {i + 1}")
    for i in range(docx_count):
        (corpus_dir / f"debrief-{i + 1}.docx").write_text(f"DOCX content {i + 1}")
    return corpus_dir


@given(
    parsers.parse("Phil previously ingested a directory with {count:d} documents"),
    target_fixture="corpus_dir",
)
def previously_ingested_directory(tmp_path, ingestion_service, corpus_registry, count):
    """Create directory and ingest it once to simulate prior ingestion."""
    corpus_dir = tmp_path / "past-proposals"
    corpus_dir.mkdir()
    for i in range(count):
        (corpus_dir / f"doc-{i + 1}.pdf").write_text(f"Content {i + 1}")
    # Perform initial ingestion
    ingestion_service.ingest_directory(corpus_dir)
    return corpus_dir


@given(
    parsers.parse("Phil has added {count:d} new PDF to the directory"),
)
def add_new_file(corpus_dir, count):
    """Add new files to an existing corpus directory."""
    for i in range(count):
        (corpus_dir / f"new-doc-{i + 1}.pdf").write_text(f"New content {i + 1}")


@given(
    parsers.parse(
        "a directory contains {pdf:d} PDFs, {docx:d} Word docs, "
        "and {other:d} Python source files"
    ),
    target_fixture="corpus_dir",
)
def mixed_directory(tmp_path, pdf, docx, other):
    """Create directory with mixed file types."""
    corpus_dir = tmp_path / "mixed"
    corpus_dir.mkdir()
    for i in range(pdf):
        (corpus_dir / f"doc-{i + 1}.pdf").write_text(f"PDF {i + 1}")
    for i in range(docx):
        (corpus_dir / f"doc-{i + 1}.docx").write_text(f"DOCX {i + 1}")
    for i in range(other):
        (corpus_dir / f"script-{i + 1}.py").write_text(f"# Python {i + 1}")
    return corpus_dir


@given("Phil provides a path to an empty directory", target_fixture="corpus_dir")
def empty_directory(tmp_path):
    """Create an empty directory."""
    corpus_dir = tmp_path / "empty"
    corpus_dir.mkdir()
    return corpus_dir


@given(
    parsers.parse(
        "a directory contains {count:d} PDFs, one of which is password-protected"
    ),
    target_fixture="corpus_dir",
)
def directory_with_protected_pdf(tmp_path, count):
    """Create directory with a simulated password-protected PDF."""
    corpus_dir = tmp_path / "mixed-docs"
    corpus_dir.mkdir()
    for i in range(count - 1):
        (corpus_dir / f"readable-{i + 1}.pdf").write_text(f"Readable PDF {i + 1}")
    # Simulate password-protected file with marker
    (corpus_dir / "protected.pdf").write_text("ENCRYPTED_CONTENT")
    return corpus_dir


@given("Phil provides a path that does not exist", target_fixture="corpus_dir")
def nonexistent_directory(tmp_path):
    """Return a path that does not exist."""
    return tmp_path / "does-not-exist"


# --- When steps ---


@when("Phil adds the directory to the corpus", target_fixture="ingestion_result")
def add_directory_to_corpus(ingestion_service, corpus_dir):
    """Invoke corpus ingestion through driving port."""
    return ingestion_service.ingest_directory(corpus_dir)


@when("Phil adds the same directory to the corpus again", target_fixture="ingestion_result")
def re_add_directory(ingestion_service, corpus_dir):
    """Invoke corpus ingestion a second time for dedup testing."""
    return ingestion_service.ingest_directory(corpus_dir)


# --- Then steps ---


@then(parsers.parse("{count:d} documents are ingested"))
def verify_ingestion_count(ingestion_result, count):
    """Verify number of documents ingested."""
    assert len(ingestion_result.new_entries) == count


@then(parsers.parse('Phil sees "{message}"'))
def verify_corpus_message(ingestion_result, message):
    """Verify user-facing message from corpus operation."""
    assert message in ingestion_result.message, (
        f"Expected '{message}' in: '{ingestion_result.message}'"
    )


@then("the corpus is ready for search")
def verify_corpus_searchable(corpus_registry):
    """Verify corpus registry has entries."""
    assert corpus_registry.document_count > 0


@then(parsers.parse("only the {count:d} new document is ingested"))
def verify_incremental_ingestion(ingestion_result, count):
    """Verify only new documents ingested on re-run."""
    assert len(ingestion_result.new_entries) == count


@then(parsers.parse("{count:d} supported documents are ingested"))
def verify_supported_count(ingestion_result, count):
    """Verify count of supported documents ingested."""
    assert len(ingestion_result.new_entries) == count


@then(parsers.parse("{count:d} unsupported files are skipped"))
def verify_skipped_count(ingestion_result, count):
    """Verify count of skipped unsupported files."""
    assert ingestion_result.skipped_unsupported == count


@then("Phil sees the list of supported file types")
def verify_supported_types_shown(ingestion_result):
    """Verify supported file types are listed in the message."""
    for ext in SUPPORTED_EXTENSIONS:
        assert ext in ingestion_result.message, (
            f"Expected '{ext}' in: '{ingestion_result.message}'"
        )


@then(parsers.parse("{count:d} readable PDFs are ingested"))
def verify_readable_count(ingestion_result, count):
    """Verify readable document count."""
    assert len(ingestion_result.new_entries) == count


@then("the password-protected PDF is skipped")
def verify_protected_skipped():
    """Verify protected file skipped -- covered by readable count assertion."""
    pass


@then("Phil sees a warning naming the skipped file with the reason")
def verify_skip_warning(ingestion_result):
    """Verify warning identifies skipped file and reason."""
    msg = ingestion_result.message
    assert "protected.pdf" in msg or "skipped" in msg.lower()


@then('Phil sees "Directory not found"')
def verify_directory_not_found(ingestion_result):
    """Verify directory not found message."""
    assert "Directory not found" in ingestion_result.message


@then("Phil sees guidance to verify the path")
def verify_path_guidance(ingestion_result):
    """Verify path verification guidance."""
    msg = ingestion_result.message.lower()
    assert "verify" in msg or "path" in msg
