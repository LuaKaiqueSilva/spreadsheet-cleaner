"""Read tabular uploads and create downloadable reports."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


def read_table(contents: bytes, filename: str, sheet_name: str | int = 0) -> pd.DataFrame:
    """Read a CSV or Excel workbook from bytes, with helpful encoding fallback."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(BytesIO(contents), sep=None, engine="python")
        except UnicodeDecodeError:
            return pd.read_csv(BytesIO(contents), sep=None, engine="python", encoding="latin-1")
    if suffix == ".xlsx":
        return pd.read_excel(BytesIO(contents), sheet_name=sheet_name)
    raise ValueError("Formato não suportado. Envie um arquivo CSV ou XLSX.")


def build_excel_report(dataframe: pd.DataFrame, report: pd.DataFrame) -> bytes:
    """Build an Excel workbook with the cleaned data and quality summary."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Dados limpos")
        report.to_excel(writer, index=False, sheet_name="Relatório")
    return output.getvalue()
