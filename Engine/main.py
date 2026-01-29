import re
import json
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple


@dataclass
class Finding:
    issue_type: str
    severity: str
    metric: str
    deck_value: str
    ir_value: str
    deck_evidence: str
    ir_evidence: str
    recommended_action: str


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_numbers_with_context(text: str) -> List[Tuple[str, str]]:
    pattern = re.compile(
        r"(?P<value>(€|\$|CHF)?\s?\d{1,3}(?:[.,]\d{1,2})?\s?(?:M|B|m|b|million|billion)?)",
        re.IGNORECASE
    )
    results: List[Tuple[str, str]] = []
    for m in pattern.finditer(_normalize_whitespace(text)):
        start = max(m.start() - 20, 0)
        end = min(m.end() + 20, len(text))
        results.append((m.group("value").strip(), text[start:end]))
    return results


def _find_metric_mentions(text: str, metric_keywords: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    out: Dict[str, List[Tuple[str, str]]] = {k: [] for k in metric_keywords}
    for metric in metric_keywords:
        pattern = re.compile(rf"({re.escape(metric)}.{{0,120}})", re.IGNORECASE | re.DOTALL)
        for m in pattern.finditer(_normalize_whitespace(text)):
            nums = _extract_numbers_with_context(m.group(1))
            for val, ev in nums:
                out[metric].append((val, ev))
    return out


def _extract_dates(text: str) -> List[str]:
    patterns = [
        r"FY\s?\d{4}",         # e.g., FY2024
        r"Q[1-4]\s?\d{4}",     # e.g., Q3 2023
        r"\b20\d{2}\b",        # e.g., 2023
    ]
    all_matches = []
    for pattern in patterns:
        all_matches.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(all_matches))  # deduplicate


def detect_definition_mismatches(deck_text: str, ir_text: str) -> List[Finding]:
    definition_keywords = [
        "includes", "excludes", "calculated as", "defined as", "comprised of", "adjusted for"
    ]
    metrics = ["arr", "mrr", "ebitda", "gross margin"]

    findings: List[Finding] = []

    for metric in metrics:
        deck_sentences = re.findall(rf"([^.]*{metric}[^.]*\.)", deck_text, re.IGNORECASE)
        ir_sentences = re.findall(rf"([^.]*{metric}[^.]*\.)", ir_text, re.IGNORECASE)

        if not deck_sentences or not ir_sentences:
            continue

        deck_def = next((s for s in deck_sentences if any(k in s.lower() for k in definition_keywords)), "")
        ir_def = next((s for s in ir_sentences if any(k in s.lower() for k in definition_keywords)), "")

        if deck_def and ir_def and deck_def.strip().lower() != ir_def.strip().lower():
            findings.append(
                Finding(
                    issue_type="definition_mismatch",
                    severity="medium",
                    metric=metric.upper(),
                    deck_value=deck_def.strip(),
                    ir_value=ir_def.strip(),
                    deck_evidence=deck_def.strip(),
                    ir_evidence=ir_def.strip(),
                    recommended_action=(
                        f"Align the definition of '{metric.upper()}' across documents to avoid investor confusion."
                    )
                )
            )

    return findings


def detect_numeric_mismatches(deck_text: str, ir_text: str) -> List[Finding]:
    metrics = ["revenue", "arr", "mrr", "ebitda", "customers", "users", "gross margin"]
    deck_hits = _find_metric_mentions(deck_text, metrics)
    ir_hits = _find_metric_mentions(ir_text, metrics)
    findings: List[Finding] = []

    for metric in metrics:
        if not deck_hits[metric] or not ir_hits[metric]:
            continue
        deck_value, deck_ev = deck_hits[metric][0]
        ir_value, ir_ev = ir_hits[metric][0]

        deck_dates = _extract_dates(deck_ev)
        ir_dates = _extract_dates(ir_ev)
        normalized_deck_dates = {d.lower().replace(" ", "") for d in deck_dates}
        normalized_ir_dates = {d.lower().replace(" ", "") for d in ir_dates}

        if deck_value.lower() == ir_value.lower() and normalized_deck_dates != normalized_ir_dates:
            findings.append(Finding(
                issue_type="date_mismatch",
                severity="medium",
                metric=metric.upper(),
                deck_value=deck_value,
                ir_value=ir_value,
                deck_evidence=deck_ev,
                ir_evidence=ir_ev,
                recommended_action="Ensure consistent date references across documents (e.g., both 'FY2024' or both 'Q4 2023')."
            ))
            continue

        if deck_value.lower() != ir_value.lower():
            findings.append(Finding(
                issue_type="numeric_mismatch",
                severity="high",
                metric=metric.upper(),
                deck_value=deck_value,
                ir_value=ir_value,
                deck_evidence=deck_ev,
                ir_evidence=ir_ev,
                recommended_action="Align the metric value across deck and IR site and add an 'as of' date or period (e.g., FY2024, Q3 2025) to remove ambiguity."
            ))

    return findings


def main():
    parser = argparse.ArgumentParser(description="Detect disclosure inconsistencies between deck and IR content.")
    parser.add_argument("--deck", required=True, help="Path to deck text file")
    parser.add_argument("--ir", required=True, help="Path to IR site text file")
    args = parser.parse_args()

    with open(args.deck, "r", encoding="utf-8") as f:
        deck_text = f.read()
    with open(args.ir, "r", encoding="utf-8") as f:
        ir_text = f.read()

    findings: List[Finding] = []
    findings += detect_numeric_mismatches(deck_text, ir_text)
    findings += detect_definition_mismatches(deck_text, ir_text)

    report = {
        "summary": {
            "total_findings": len(findings),
            "types": sorted(list({f.issue_type for f in findings})),
        },
        "findings": [asdict(f) for f in findings],
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
