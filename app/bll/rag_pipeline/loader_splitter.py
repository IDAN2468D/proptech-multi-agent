import io
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class DocumentChunk:
    """Represents a semantically split PDF chunk with mandatory page citation."""

    chunk_id: str
    source_document: str
    page_number: int
    text: str


class LegalPDFLoaderSplitter:
    """
    Extracts text and page numbers from PDF bytes (Tabu extracts, sale contracts, appraisals)
    and splits them into overlapping semantic legal segments while preserving page citations.
    """

    def __init__(self, chunk_size: int = 550, chunk_overlap: int = 100) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_pages(self, file_bytes: bytes) -> list[tuple[int, str]]:
        """Extract (page_number, text) tuples from PDF bytes or structured text fallback."""
        pages: list[tuple[int, str]] = []
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(file_bytes))
            for idx, page in enumerate(reader.pages, start=1):
                extracted = (page.extract_text() or "").strip()
                if extracted:
                    pages.append((idx, extracted))
        except Exception:
            pass

        if not pages:
            # Fallback for raw text / synthetic test PDFs with optional [PAGE X] markers
            raw_text = file_bytes.decode("utf-8", errors="ignore").strip()
            page_splits = re.split(r"\[PAGE\s+(\d+)\]", raw_text)
            if len(page_splits) > 1:
                # Format: prefix, page_num, text, page_num, text...
                idx = 1
                while idx < len(page_splits):
                    p_num = int(page_splits[idx])
                    p_txt = page_splits[idx + 1].strip()
                    if p_txt:
                        pages.append((p_num, p_txt))
                    idx += 2
            elif raw_text:
                pages.append((1, raw_text))

        return pages

    def split_pages_into_chunks(
        self,
        file_bytes: bytes,
        filename: str,
    ) -> tuple[list[DocumentChunk], int]:
        """Return list of DocumentChunk and total pages extracted."""
        pages = self.extract_pages(file_bytes)
        chunks: list[DocumentChunk] = []
        chunk_counter = 1

        for page_num, page_text in pages:
            normalized = re.sub(r"\s+", " ", page_text).strip()
            if len(normalized) <= self.chunk_size:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{filename}#p{page_num}_c{chunk_counter}",
                        source_document=filename,
                        page_number=page_num,
                        text=normalized,
                    )
                )
                chunk_counter += 1
            else:
                start = 0
                step = max(1, self.chunk_size - self.chunk_overlap)
                while start < len(normalized):
                    segment = normalized[start : start + self.chunk_size].strip()
                    if segment:
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"{filename}#p{page_num}_c{chunk_counter}",
                                source_document=filename,
                                page_number=page_num,
                                text=segment,
                            )
                        )
                        chunk_counter += 1
                    if start + self.chunk_size >= len(normalized):
                        break
                    start += step

        return chunks, len(pages)
