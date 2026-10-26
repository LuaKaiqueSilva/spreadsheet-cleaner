"""Streamlit interface for the spreadsheet cleaner."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from spreadsheet_cleaner.cleaning import CleaningOptions, clean_dataframe, quality_report
from spreadsheet_cleaner.io import build_excel_report, read_table


ROOT = Path(__file__).parent
SAMPLE_PATH = ROOT / "examples" / "vendas_exemplo.csv"

st.set_page_config(page_title="Planilha Clara", page_icon="🧹", layout="wide")
st.title("🧹 Planilha Clara")
st.caption("Limpeza rápida e local de arquivos CSV e Excel.")

with st.sidebar:
    st.header("Arquivo")
    use_sample = st.toggle("Usar planilha de demonstração", value=True)
    uploaded_file = None if use_sample else st.file_uploader(
        "Selecione um arquivo", type=["csv", "xlsx"], help="Tamanho máximo: 20 MB."
    )
    st.subheader("O que limpar")
    remove_empty_rows = st.checkbox("Remover linhas vazias", value=True)
    remove_duplicates = st.checkbox("Remover linhas duplicadas", value=False)
    remove_empty_columns = st.checkbox("Remover colunas vazias", value=True)
    trim_whitespace = st.checkbox("Aparar espaços em células", value=True)
    normalize_headers = st.checkbox("Padronizar cabeçalhos", value=True)
    st.divider()
    st.caption("Os arquivos são processados nesta máquina e não são enviados a uma API externa.")

try:
    if use_sample:
        source = SAMPLE_PATH.read_bytes()
        filename = SAMPLE_PATH.name
    elif uploaded_file is not None:
        if uploaded_file.size > 20 * 1024 * 1024:
            st.error("O arquivo excede o limite de 20 MB.")
            st.stop()
        source = uploaded_file.getvalue()
        filename = uploaded_file.name
    else:
        st.info("Ative a demonstração ou envie um arquivo CSV/XLSX na barra lateral.")
        st.stop()

    if filename.lower().endswith(".xlsx"):
        workbook = pd.ExcelFile(source)
        selected_sheet = st.selectbox("Aba da planilha", workbook.sheet_names)
        original = read_table(source, filename, selected_sheet)
    else:
        original = read_table(source, filename)

    options = CleaningOptions(
        remove_empty_rows=remove_empty_rows,
        remove_duplicate_rows=remove_duplicates,
        remove_empty_columns=remove_empty_columns,
        trim_whitespace=trim_whitespace,
        normalize_headers=normalize_headers,
    )
    result = clean_dataframe(original, options)
    report = quality_report(result)

    st.subheader("Resumo da limpeza")
    metrics = st.columns(4)
    metrics[0].metric("Linhas finais", len(result.dataframe))
    metrics[1].metric("Duplicatas removidas", result.removed_duplicate_rows)
    metrics[2].metric("Linhas vazias removidas", result.removed_empty_rows)
    metrics[3].metric("Células aparadas", result.trimmed_cells)

    st.caption("Confira a prévia e as linhas que serão removidas antes de baixar o resultado.")
    input_tab, preview_tab, removed_tab, report_tab = st.tabs(
        ["Original", "Prévia limpa", "Linhas removidas", "Relatório de qualidade"]
    )
    with input_tab:
        st.dataframe(original.head(100), width="stretch", hide_index=True)
        if len(original) > 100:
            st.caption("Prévia limitada às primeiras 100 linhas.")
    with preview_tab:
        st.dataframe(result.dataframe.head(100), width="stretch", hide_index=True)
        if len(result.dataframe) > 100:
            st.caption("Prévia limitada às primeiras 100 linhas.")
    with removed_tab:
        if result.removed_columns:
            st.info("Colunas vazias que serão removidas: " + ", ".join(result.removed_columns))
        if result.removed_rows.empty:
            if not result.removed_columns:
                st.success("Nenhuma linha ou coluna será removida com as opções selecionadas.")
            else:
                st.success("Nenhuma linha será removida com as opções selecionadas.")
        else:
            st.warning(
                f"{len(result.removed_rows)} linha(s) serão removidas. A remoção de duplicatas "
                "só acontece quando essa opção está ativada."
            )
            st.dataframe(result.removed_rows.head(100), width="stretch", hide_index=True)
            if len(result.removed_rows) > 100:
                st.caption("Prévia limitada às primeiras 100 linhas removidas.")
    with report_tab:
        st.dataframe(report, width="stretch", hide_index=True)

    cleaned_csv = result.dataframe.to_csv(index=False).encode("utf-8-sig")
    cleaned_xlsx = build_excel_report(result.dataframe, report)
    base_name = Path(filename).stem
    st.subheader("Baixar resultado")
    downloads = st.columns(2)
    downloads[0].download_button(
        "Baixar CSV limpo", cleaned_csv, file_name=f"{base_name}_limpo.csv", mime="text/csv"
    )
    downloads[1].download_button(
        "Baixar Excel + relatório", cleaned_xlsx,
        file_name=f"{base_name}_relatorio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except (ValueError, UnicodeError, OSError, ImportError) as error:
    st.error(f"Não consegui ler esse arquivo: {error}")
