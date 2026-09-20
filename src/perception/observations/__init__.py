# Atomic text observations (P1)
from .atomic_text import (
    AtomicTextObservation,
    extract_page_observations,
    extract_pdf_observations,
    observations_to_json,
    pymupdf_version,
    SOURCE_CHAR, SOURCE_WORD, SOURCE_SPAN, SOURCE_LINE, SOURCE_BLOCK,
)
