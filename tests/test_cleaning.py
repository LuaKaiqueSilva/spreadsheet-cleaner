from __future__ import annotations

import unittest

import pandas as pd

from spreadsheet_cleaner.cleaning import CleaningOptions, clean_dataframe


class CleaningTests(unittest.TestCase):
    def test_duplicate_rows_are_preserved_by_default(self) -> None:
        source = pd.DataFrame({"Pedido": [10, 10], "Cliente": ["Ana", "Ana"]})

        result = clean_dataframe(source)

        self.assertEqual(len(result.dataframe), 2)
        self.assertEqual(result.removed_duplicate_rows, 0)
        self.assertTrue(result.removed_rows.empty)

    def test_duplicate_rows_can_be_removed_and_previewed(self) -> None:
        source = pd.DataFrame({"Pedido": [10, 10], "Cliente": ["Ana", "Ana"]})

        result = clean_dataframe(source, CleaningOptions(remove_duplicate_rows=True))

        self.assertEqual(len(result.dataframe), 1)
        self.assertEqual(result.removed_duplicate_rows, 1)
        self.assertEqual(result.removed_rows.iloc[0]["Pedido"], 10)

    def test_empty_rows_and_columns_are_reported(self) -> None:
        source = pd.DataFrame(
            {"Nome": [" Ana ", " ", "Bia"], "Vazio": [None, None, None]},
        )

        result = clean_dataframe(source)

        self.assertEqual(len(result.dataframe), 2)
        self.assertEqual(result.removed_empty_rows, 1)
        self.assertEqual(result.removed_empty_columns, 1)
        self.assertEqual(result.removed_columns, ("Vazio",))
        self.assertEqual(len(result.removed_rows), 1)

    def test_operations_can_be_disabled(self) -> None:
        source = pd.DataFrame({" Nome do Cliente ": [" Ana ", " Ana "], "Vazio": [None, None]})
        options = CleaningOptions(
            remove_empty_rows=False,
            remove_duplicate_rows=False,
            remove_empty_columns=False,
            trim_whitespace=False,
            normalize_headers=False,
        )

        result = clean_dataframe(source, options)

        self.assertEqual(list(result.dataframe.columns), list(source.columns))
        self.assertEqual(result.dataframe.iloc[0, 0], " Ana ")
        self.assertEqual(len(result.dataframe), 2)
        self.assertEqual(result.removed_empty_columns, 0)
        self.assertEqual(result.trimmed_cells, 0)
        self.assertEqual(result.renamed_columns, 0)

    def test_headers_are_normalized_and_kept_unique(self) -> None:
        source = pd.DataFrame([[1, 2]], columns=["Preço total", "Preco total"])

        result = clean_dataframe(source)

        self.assertEqual(list(result.dataframe.columns), ["preco_total", "preco_total_2"])
        self.assertEqual(result.renamed_columns, 2)


if __name__ == "__main__":
    unittest.main()
