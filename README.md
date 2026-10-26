# Planilha Clara

Ferramenta local para limpar arquivos CSV e Excel de pequenos negócios. O painel mostra uma prévia dos dados, explica as alterações e exporta CSV limpo ou um Excel com os dados e um relatório de qualidade.

## O que faz

- Permite escolher quais regras de limpeza aplicar antes de exportar.
- Remove linhas totalmente vazias e colunas sem dados quando selecionado.
- Só remove linhas duplicadas quando essa opção é ativada; ela começa desativada para preservar registros potencialmente legítimos.
- Aparar espaços no começo e fim de valores de texto.
- Padroniza cabeçalhos, remove acentos e evita nomes de coluna repetidos, quando selecionado.
- Mostra um resumo do que foi alterado antes de baixar.
- Exibe prévias dos dados originais, do resultado e das linhas/colunas que serão removidas.
- Lê CSV com separador automático e suporte a arquivos Excel com múltiplas abas.
- Processa os arquivos localmente; não usa serviços externos.

## Requisitos

- Python 3.11 ou superior.

## Instalação

Linux/macOS:

```bash
git clone https://github.com/LuaKaiqueSilva/spreadsheet-cleaner.git
cd spreadsheet-cleaner
./scripts/setup.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/LuaKaiqueSilva/spreadsheet-cleaner.git
cd spreadsheet-cleaner
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Executar

Linux/macOS:

```bash
./scripts/run.sh
```

Windows, com o ambiente virtual ativado:

```powershell
streamlit run app.py
```

O Streamlit mostra o endereço local no terminal. A demonstração começa ativada; desative a opção na barra lateral para enviar seu próprio CSV ou XLSX.

## Exemplo de uso

1. Abra o painel e confira a planilha de demonstração.
2. Veja as linhas e os cabeçalhos após a limpeza.
3. Na barra lateral, escolha as regras de limpeza. Duplicatas começam desativadas.
4. Confira as abas `Original`, `Prévia limpa`, `Linhas removidas` e `Relatório de qualidade`.
5. Baixe o CSV limpo ou o Excel com as abas `Dados limpos` e `Relatório`.

## Desenvolvimento

Execute os testes automatizados com:

```bash
python -m unittest discover -s tests -v
```

## Limitações

O projeto não tenta adivinhar regras específicas do negócio nem altera formatos de datas e valores. Faça uma cópia dos seus dados e confira o resultado antes de usá-lo em processos importantes. Arquivos `.xls` antigos não são aceitos nesta versão.
