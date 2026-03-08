"""Step definitions for corpus ingestion (US-003).

Invokes through: Corpus ingestion service (driving port).
Does NOT import internal file parsers or hash utilities directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature file
scenarios("../features/corpus_ingestion.feature")


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
def previously_ingested_directory(tmp_path, count):
    """Create directory simulating prior ingestion."""
    corpus_dir = tmp_path / "past-proposals"
    corpus_dir.mkdir()
    for i in range(count):
        (corpus_dir / f"doc-{i + 1}.pdf").write_text(f"Content {i + 1}")
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


@when("Phil adds the directory to the corpus")
def add_directory_to_corpus(corpus_dir):
    """Invoke corpus ingestion through driving port."""
    # TODO: Invoke through CorpusIngestionService when implemented
    pytest.skip("Awaiting CorpusIngestionService implementation")


@when("Phil adds the same directory to the corpus again")
def re_add_directory(corpus_dir):
    """Invoke corpus ingestion a second time for dedup testing."""
    # TODO: Invoke through CorpusIngestionService
    pytest.skip("Awaiting CorpusIngestionService implementation")


# --- Then steps ---


@then(parsers.parse("{count:d} documents are ingested"))
def verify_ingestion_count(count):
    """Verify number of documents ingested."""
    pass


@then(parsers.parse('Phil sees "{message}"'))
def verify_corpus_message(message):
    """Verify user-facing message from corpus operation."""
    pass


@then("the corpus is ready for search")
def verify_corpus_searchable():
    """Verify corpus metadata updated for search."""
    pass


@then(parsers.parse("only the {count:d} new document is ingested"))
def verify_incremental_ingestion(count):
    """Verify only new documents ingested on re-run."""
    pass


@then(parsers.parse("{count:d} supported documents are ingested"))
def verify_supported_count(count):
    """Verify count of supported documents ingested."""
    pass


@then(parsers.parse("{count:d} unsupported files are skipped"))
def verify_skipped_count(count):
    """Verify count of skipped unsupported files."""
    pass


@then("Phil sees the list of supported file types")
def verify_supported_types_shown():
    """Verify supported file types are listed."""
    pass


@then(parsers.parse("{count:d} readable PDFs are ingested"))
def verify_readable_count(count):
    """Verify readable document count."""
    pass


@then("the password-protected PDF is skipped")
def verify_protected_skipped():
    """Verify protected file skipped."""
    pass


@then("Phil sees a warning naming the skipped file with the reason")
def verify_skip_warning():
    """Verify warning identifies skipped file and reason."""
    pass


@then("Phil sees guidance to verify the path")
def verify_path_guidance():
    """Verify path verification guidance."""
    pass
