"""Data cleaning and quality reporting for CSV and Excel tables."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CleaningResult:
    dataframe: pd.DataFrame
    original_rows: int
    removed_empty_rows: int
    removed_duplicate_rows: int
    removed_empty_columns: int
    trimmed_cells: int
    renamed_columns: int


def normalize_column_name(value: object, position: int) -> str:
    """Convert a column label to a readable, unique-friendly name."""
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_").lower()
    return text or f"coluna_{position + 1}"


def clean_dataframe(dataframe: pd.DataFrame) -> CleaningResult:
    """Trim text, normalize headers and remove fully empty and duplicate rows."""
    frame = dataframe.copy()
    original_rows = len(frame)
    original_columns = list(frame.columns)

    frame = frame.dropna(axis=1, how="all")
    removed_empty_columns = len(original_columns) - len(frame.columns)
    trimmed_cells = 0
    for column in frame.columns:
        if pd.api.types.is_object_dtype(frame[column]) or pd.api.types.is_string_dtype(frame[column]):
            before = frame[column].copy()
            frame[column] = frame[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
            trimmed_cells += int(
                ((before != frame[column]) & before.notna()).sum()
            )

    empty_rows = frame.isna().all(axis=1) | frame.fillna("").eq("").all(axis=1)
    removed_empty_rows = int(empty_rows.sum())
    frame = frame.loc[~empty_rows].copy()
    before_deduplication = len(frame)
    frame = frame.drop_duplicates().reset_index(drop=True)
    removed_duplicate_rows = before_deduplication - len(frame)

    normalized = [normalize_column_name(column, index) for index, column in enumerate(frame.columns)]
    counts: dict[str, int] = {}
    unique_names = []
    for name in normalized:
        counts[name] = counts.get(name, 0) + 1
        unique_names.append(name if counts[name] == 1 else f"{name}_{counts[name]}")
    renamed_columns = sum(str(old) != new for old, new in zip(frame.columns, unique_names))
    frame.columns = unique_names

    return CleaningResult(
        dataframe=frame,
        original_rows=original_rows,
        removed_empty_rows=removed_empty_rows,
        removed_duplicate_rows=removed_duplicate_rows,
        removed_empty_columns=removed_empty_columns,
        trimmed_cells=trimmed_cells,
        renamed_columns=renamed_columns,
    )


def quality_report(result: CleaningResult) -> pd.DataFrame:
    """Create a compact Portuguese summary of applied cleaning operations."""
    return pd.DataFrame(
        [
            {"Verificação": "Linhas recebidas", "Quantidade": result.original_rows},
            {"Verificação": "Linhas vazias removidas", "Quantidade": result.removed_empty_rows},
            {"Verificação": "Linhas duplicadas removidas", "Quantidade": result.removed_duplicate_rows},
            {"Verificação": "Colunas vazias removidas", "Quantidade": result.removed_empty_columns},
            {"Verificação": "Células com espaços aparados", "Quantidade": result.trimmed_cells},
            {"Verificação": "Cabeçalhos normalizados", "Quantidade": result.renamed_columns},
            {"Verificação": "Linhas finais", "Quantidade": len(result.dataframe)},
        ]
    )
