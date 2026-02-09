"""PDF splitting utilities for coco.

This implements a simple page-based splitter using pypdf (PyPDF2 successor).
It extracts pages into separate PDF files according to simple heuristics:
- The EDD, RES, RECI pages are identified by searching text that contains keywords.
- Invoice pages (factures) are extracted as single-page PDFs when the page contains the word "FACTURE" or "Montant" or an invoice-like pattern.

Duplicate detection: identical pages (byte-equal) are considered duplicates and moved to doublons.

Notes: This is a pragmatic implementation to bootstrap the tool; further improvements can
use OCR or layout heuristics.
"""
from __future__ import annotations

import os
import re

try:
    from pypdf import PdfReader, PdfWriter
except Exception:  # pragma: no cover - pypdf may be missing in some environments
    # Provide helpful error when library is missing at runtime
    PdfReader = None  # type: ignore
    PdfWriter = None  # type: ignore


def _ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def _sanitize_filename(s: str) -> str:
    # Remove path-unsafe characters
    return re.sub(r"[^A-Za-z0-9\-_.]", "", s)


def _extract_invoice_metadata(text: str):
    """Try to extract company, date (YYYY/MM/DD or variants) and amount from page text.

    Returns (company, year, month, day, amount) with None when not found.
    """
    company = None
    date_y = None
    date_m = None
    date_d = None
    amount = None

    # Heuristics for amount: look for euro amounts like 1234.56 or 1 234,56 or 1234,56 €
    m_amt = re.search(r"([0-9]{1,3}(?:[ \\u00A0][0-9]{3})*(?:[,.][0-9]{2})?)\\s*(€|eur|euro)?", text, re.IGNORECASE)
    if m_amt:
        amt = m_amt.group(1)
        amt = amt.replace(" ", "").replace('\\u00A0', '').replace(',', '.')
        try:
            amount = f"{float(amt):.2f}"
        except Exception:
            amount = None

    # Date heuristic: YYYY-MM-DD or DD/MM/YYYY or DD.MM.YYYY
    m_date = re.search(r"(20[0-9]{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])", text)
    if not m_date:
        m_date = re.search(r"(0[1-9]|[12][0-9]|3[01])[-/\\.](0[1-9]|1[0-2])[-/\\.](20[0-9]{2})", text)
        if m_date:
            date_d, date_m, date_y = m_date.group(1), m_date.group(2), m_date.group(3)
    else:
        date_y, date_m, date_d = m_date.group(1), m_date.group(2), m_date.group(3)

    # Company heuristic: look for lines with 'SARL', 'SAS', 'SA', 'EURL' or capitalized words near top
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines[:8]:
        if re.search(r"\\b(SARL|SAS|SA|EURL|SNC)\\b", l, re.IGNORECASE):
            company = l
            break
    if not company and lines:
        # fallback to first longish line
        for l in lines[:8]:
            if len(l) > 4 and not re.search(r"\\b\\d{2,}\\b", l):
                company = l
                break

    return company, date_y, date_m, date_d, amount


def split_pdf(path: str, out_folder: str, account_year_end: str) -> dict:
    """Split the PES PDF into EDD, RES, RECI, invoices, extras and duplicates.

    Returns a dict with keys: edd, res, reci, invoices (list), extras (list), doublons (list)
    Each value is a list of generated file paths (or single path for edd/res/reci if found).

    account_year_end is the final year used for naming invoices, e.g., "2025" for "2024-2025".
    """
    if PdfReader is None:
        raise RuntimeError("pypdf (pypdf) library is required: pip install pypdf")

    reader = PdfReader(path)
    n = len(reader.pages)

    base_out = out_folder or os.getcwd()
    _ensure_dir(base_out)

    invoices_dir = os.path.join(base_out, "factures_a_controler")
    extras_dir = os.path.join(base_out, "extra")
    doublons_dir = os.path.join(base_out, "doublons")
    _ensure_dir(invoices_dir)
    _ensure_dir(extras_dir)
    _ensure_dir(doublons_dir)

    edd_writer = None
    res_writer = None
    reci_writer = None
    edd_path = None
    res_path = None
    reci_path = None

    invoices = []
    extras = []
    doublons = []

    seen_hashes = {}

    for i in range(n):
        page = reader.pages[i]
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        low = text.lower()

        # classify
        if "état des dépenses" in low or "etat des depenses" in low or "edd" in low:
            if edd_writer is None:
                edd_writer = PdfWriter()
                edd_path = os.path.join(base_out, f"EDD_{account_year_end}.pdf")
            edd_writer.add_page(page)
            continue
        if "repart" in low and "eau" in low and "synd" in low:
            if res_writer is None:
                res_writer = PdfWriter()
                res_path = os.path.join(base_out, f"RES_{account_year_end}.pdf")
            res_writer.add_page(page)
            continue
        if "compteurs" in low and "eau" in low:
            if reci_writer is None:
                reci_writer = PdfWriter()
                reci_path = os.path.join(base_out, f"RECI_{account_year_end}.pdf")
            reci_writer.add_page(page)
            continue

        # invoice detection
        if "facture" in low or "montant" in low or "tva" in low:
            company, y, m, d, amt = _extract_invoice_metadata(text)
            company_clean = _sanitize_filename(company) if company else "Unknown"
            y = y or account_year_end
            m = m or "MM"
            d = d or "DD"
            amt = amt or "0.00"
            fname = f"F{account_year_end}_p{i+1}_{company_clean}_{y}_{m}_{d}__{amt}.pdf"
            out_path = os.path.join(invoices_dir, fname)

            # detect duplicates using normalized text hash
            key = (company_clean, y, m, d, amt, re.sub(r"\\s+", " ", text).strip()[:200])
            if key in seen_hashes:
                # duplicate
                dup_path = os.path.join(doublons_dir, fname)
                w = PdfWriter()
                w.add_page(page)
                with open(dup_path, "wb") as fh:
                    w.write(fh)
                doublons.append(dup_path)
            else:
                seen_hashes[key] = out_path
                w = PdfWriter()
                w.add_page(page)
                with open(out_path, "wb") as fh:
                    w.write(fh)
                invoices.append(out_path)
            continue

        # else: extra
        fname = f"extra_p{i+1}.pdf"
        out_path = os.path.join(extras_dir, fname)
        w = PdfWriter()
        w.add_page(page)
        with open(out_path, "wb") as fh:
            w.write(fh)
        extras.append(out_path)

    # flush multi-page writers
    if edd_writer and edd_path:
        with open(edd_path, "wb") as fh:
            edd_writer.write(fh)
    if res_writer and res_path:
        with open(res_path, "wb") as fh:
            res_writer.write(fh)
    if reci_writer and reci_path:
        with open(reci_path, "wb") as fh:
            reci_writer.write(fh)

    return {
        "edd": [edd_path] if edd_path else [],
        "res": [res_path] if res_path else [],
        "reci": [reci_path] if reci_path else [],
        "invoices": invoices,
        "extras": extras,
        "doublons": doublons,
    }


def _page_bytes(page) -> bytes:
    """Return a byte representation of the page to detect duplicates.

    We use the raw content stream if available; fallback to text.
    """
    # pypdf Page has get_contents / get_object... but simplest is extract_text
    try:
        txt = page.extract_text() or ""
        return txt.encode("utf-8")
    except Exception:
        try:
            raw = page.get_contents()
            return bytes(raw)
        except Exception:
            return b""
