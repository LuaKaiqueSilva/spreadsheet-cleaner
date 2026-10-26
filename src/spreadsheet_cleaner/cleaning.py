"""Data cleaning and quality reporting for CSV and Excel tables."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CleaningOptions:
    remove_empty_rows: bool = True
    remove_duplicate_rows: bool = False
    remove_empty_columns: bool = True
    trim_whitespace: bool = True
    normalize_headers: bool = True


@dataclass(frozen=True)
class CleaningResult:
    dataframe: pd.DataFrame
    original_rows: int
    removed_empty_rows: int
    removed_duplicate_rows: int
    removed_empty_columns: int
    trimmed_cells: int
    renamed_columns: int
    removed_rows: pd.DataFrame
    removed_columns: tuple[str, ...]


def normalize_column_name(value: object, position: int) -> str:
    """Convert a column label to a readable, unique-friendly name."""
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_").lower()
    return text or f"coluna_{position + 1}"


def clean_dataframe(
    dataframe: pd.DataFrame, options: CleaningOptions | None = None
) -> CleaningResult:
    """Clean a table according to the selected operations and retain removed rows for review."""
    options = options or CleaningOptions()
    source = dataframe.copy().reset_index(drop=True)
    frame = source.copy()
    original_rows = len(frame)
    original_columns = list(frame.columns)

    removed_columns = tuple(
        str(frame.columns[position])
        for position in range(len(frame.columns))
        if frame.iloc[:, position].isna().all()
    ) if options.remove_empty_columns else ()
    if options.remove_empty_columns:
        frame = frame.dropna(axis=1, how="all")
    removed_empty_columns = len(original_columns) - len(frame.columns)
    trimmed_cells = 0
    if options.trim_whitespace:
        for column in frame.columns:
            if pd.api.types.is_object_dtype(frame[column]) or pd.api.types.is_string_dtype(frame[column]):
                before = frame[column].copy()
                frame[column] = frame[column].map(
                    lambda value: value.strip() if isinstance(value, str) else value
                )
                trimmed_cells += int(((before != frame[column]) & before.notna()).sum())

    blank_values = frame.apply(
        lambda column: column.map(lambda value: not value.strip() if isinstance(value, str) else pd.isna(value))
    )
    empty_rows = blank_values.all(axis=1) if len(frame.columns) else pd.Series(True, index=frame.index)
    rows_to_remove = pd.Series(False, index=frame.index)
    removed_empty_rows = int(empty_rows.sum()) if options.remove_empty_rows else 0
    if options.remove_empty_rows:
        rows_to_remove |= empty_rows

    candidate = frame.loc[~rows_to_remove].copy()
    duplicate_rows = candidate.duplicated(keep="first")
    removed_duplicate_rows = int(duplicate_rows.sum()) if options.remove_duplicate_rows else 0
    if options.remove_duplicate_rows:
        rows_to_remove.loc[candidate.index[duplicate_rows]] = True
    removed_rows = source.loc[rows_to_remove[rows_to_remove].index].copy()
    frame = frame.loc[~rows_to_remove].reset_index(drop=True)

    renamed_columns = 0
    if options.normalize_headers:
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
        removed_rows=removed_rows,
        removed_columns=removed_columns,
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
