# Task 009: Criar Importador de Modelo de Contrato

Status: pending

## Descrição

Implementar ferramenta de importação que converte planilhas XLSX estruturadas em arquivos JSON formatados para importação de modelos de contrato no sistema.

### Contexto

O sistema precisa importar modelos de contratos estruturados (cláusulas, subcláusulas, tags) que geralmente são mantidos em planilhas Excel. Atualmente:

- ❌ Não existe ferramenta automatizada de importação
- ❌ Criação manual de JSON é propensa a erros
- ❌ Processo lento e não escalável

Esta ferramenta deve:

- ✅ Ler planilhas XLSX com estrutura definida
- ✅ Validar dados e estrutura
- ✅ Gerar JSON no formato esperado pelo sistema
- ✅ Incluir validações e tratamento de erros

## 🎯 Objetivo Principal

Criar script/ferramenta CLI que:

1. Leia planilha XLSX com estrutura de cláusulas e subcláusulas
2. Valide formato e dados obrigatórios
3. Gere JSON estruturado compatível com o formato de importação
4. Forneça feedback claro de erros e warnings

## 📋 Especificação da Planilha de Entrada

### Estrutura Esperada

A planilha deve conter as seguintes colunas:

| Coluna              | Tipo     | Obrigatório | Descrição                                    | Exemplo                  |
| ------------------- | -------- | ----------- | -------------------------------------------- | ------------------------ |
| `numero_clausula`   | `string` | ✅          | Número da cláusula principal                 | "1.0", "2.0"             |
| `titulo_clausula`   | `string` | ✅          | Título da cláusula                           | "OBJETO DO CONTRATO"     |
| `numero_subclusula` | `string` | ❌          | Número da subcláusula (se houver)            | "1.1", "2.3"             |
| `conteudo`          | `string` | ✅          | Texto do conteúdo da (sub)cláusula           | "O presente contrato..." |
| `tag`               | `string` | ❌          | Nome da tag associada (sem delimitadores {}) | "objeto", "prazo"        |
| `observacoes`       | `string` | ❌          | Observações adicionais (não importadas)      | "Revisar redação"        |

### Regras de Negócio

1. **Hierarquia**: Cláusulas podem ter zero ou mais subcláusulas
2. **Numeração**: Subcláusulas devem pertencer a uma cláusula existente (ex: 1.1 pertence a 1.0)
3. **Tags**: São opcionais, mas quando presentes devem ser único texto sem `{{` ou `}}`
4. **Conteúdo vazio**: Linhas com conteúdo vazio são ignoradas com warning

## 📦 Especificação do JSON de Saída

### Estrutura

```json
{
  "modelo_contrato": {
    "nome": "Contrato SAP Serviços",
    "descricao": "Modelo de contrato para serviços SAP",
    "versao": "1.0"
  },
  "clausulas": [
    {
      "numero": "1.0",
      "titulo": "OBJETO DO CONTRATO",
      "conteudo": "O presente contrato tem por objeto...",
      "tag": "objeto",
      "subcluasulas": [
        {
          "numero": "1.1",
          "conteudo": "São considerados serviços...",
          "tag": null
        }
      ]
    }
  ]
}
```

### Mapeamento

```
Planilha (linha com numero_subclusula vazio)
  ↓
{
  "numero": numero_clausula,
  "titulo": titulo_clausula,
  "conteudo": conteudo,
  "tag": tag,
  "subcluasulas": []
}

Planilha (linha com numero_subclusula preenchido)
  ↓
Adiciona em clausulas[].subcluasulas[]:
{
  "numero": numero_subclusula,
  "conteudo": conteudo,
  "tag": tag
}
```

## 🏗️ Implementação

### Interface CLI

```bash
# Uso básico
python versiona_cli.py importar-modelo \
  --planilha "./assets/contrato.xlsx" \
  --output "./modelo-contrato.json"

# Com validação estrita
python versiona_cli.py importar-modelo \
  --planilha "./assets/contrato.xlsx" \
  --output "./modelo-contrato.json" \
  --strict

# Apenas validar sem gerar output
python versiona_cli.py importar-modelo \
  --planilha "./assets/contrato.xlsx" \
  --validate-only
```

### Estrutura do Código

```python
# versiona_cli.py (adicionar comando)

import click
from versiona-ai.importador_modelo import ImportadorModelo

@cli.command('importar-modelo')
@click.option('--planilha', required=True, help='Caminho da planilha XLSX')
@click.option('--output', required=True, help='Caminho do JSON de saída')
@click.option('--strict', is_flag=True, help='Modo estrito: falha em warnings')
@click.option('--validate-only', is_flag=True, help='Apenas validar estrutura')
def importar_modelo(planilha: str, output: str, strict: bool, validate_only: bool):
    """
    Importa modelo de contrato a partir de planilha XLSX.
    """
    try:
        importador = ImportadorModelo(planilha, strict=strict)

        # Validar
        importador.validar()

        if validate_only:
            click.echo("✅ Planilha válida!")
            return

        # Processar e gerar JSON
        modelo = importador.processar()
        importador.salvar_json(modelo, output)

        click.echo(f"✅ JSON gerado com sucesso: {output}")

    except Exception as e:
        click.echo(f"❌ Erro: {e}", err=True)
        raise click.Abort()
```

### Classe ImportadorModelo

```python
# versiona-ai/importador_modelo.py

import pandas as pd
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Clausula:
    numero: str
    titulo: str
    conteudo: str
    tag: Optional[str]
    subcluasulas: List['Subcluasula']

@dataclass
class Subcluasula:
    numero: str
    conteudo: str
    tag: Optional[str]

class ImportadorModelo:
    """
    Importa modelo de contrato a partir de planilha XLSX.
    """

    COLUNAS_OBRIGATORIAS = [
        'numero_clausula',
        'titulo_clausula',
        'conteudo'
    ]

    def __init__(self, caminho_planilha: str, strict: bool = False):
        self.caminho = caminho_planilha
        self.strict = strict
        self.warnings: List[str] = []
        self.df: Optional[pd.DataFrame] = None

    def validar(self) -> bool:
        """
        Valida estrutura da planilha.
        """
        # 1. Ler planilha
        self.df = pd.read_excel(self.caminho)

        # 2. Validar colunas obrigatórias
        for col in self.COLUNAS_OBRIGATORIAS:
            if col not in self.df.columns:
                raise ValueError(f"Coluna obrigatória ausente: {col}")

        # 3. Validar dados
        for idx, row in self.df.iterrows():
            self._validar_linha(idx, row)

        # 4. Se strict e há warnings, falhar
        if self.strict and self.warnings:
            raise ValueError(f"Validação falhou:\n" + "\n".join(self.warnings))

        return True

    def _validar_linha(self, idx: int, row: pd.Series):
        """
        Valida uma linha da planilha.
        """
        linha = idx + 2  # +2 porque Excel começa em 1 e tem header

        # Conteúdo vazio
        if pd.isna(row['conteudo']) or str(row['conteudo']).strip() == '':
            self.warnings.append(f"Linha {linha}: conteúdo vazio")

        # Numeração de subcláusula sem cláusula pai
        if not pd.isna(row.get('numero_subclusula')):
            num_sub = str(row['numero_subclusula'])
            num_clausula = str(row['numero_clausula'])
            if not num_sub.startswith(num_clausula):
                self.warnings.append(
                    f"Linha {linha}: subcláusula {num_sub} não pertence à cláusula {num_clausula}"
                )

    def processar(self) -> Dict:
        """
        Processa planilha e retorna estrutura JSON.
        """
        if self.df is None:
            self.validar()

        clausulas = []
        clausula_atual = None

        for _, row in self.df.iterrows():
            # Ignorar linhas vazias
            if pd.isna(row['conteudo']) or str(row['conteudo']).strip() == '':
                continue

            # Se não tem subcláusula, é cláusula principal
            if pd.isna(row.get('numero_subclusula')):
                # Salvar cláusula anterior se existir
                if clausula_atual:
                    clausulas.append(clausula_atual)

                # Criar nova cláusula
                clausula_atual = {
                    "numero": str(row['numero_clausula']),
                    "titulo": str(row['titulo_clausula']),
                    "conteudo": str(row['conteudo']),
                    "tag": str(row['tag']) if not pd.isna(row.get('tag')) else None,
                    "subcluasulas": []
                }
            else:
                # Adicionar subcláusula à cláusula atual
                if clausula_atual is None:
                    raise ValueError(f"Subcláusula {row['numero_subclusula']} sem cláusula pai")

                clausula_atual['subcluasulas'].append({
                    "numero": str(row['numero_subclusula']),
                    "conteudo": str(row['conteudo']),
                    "tag": str(row['tag']) if not pd.isna(row.get('tag')) else None
                })

        # Adicionar última cláusula
        if clausula_atual:
            clausulas.append(clausula_atual)

        return {
            "modelo_contrato": {
                "nome": "Modelo Importado",
                "descricao": f"Importado de {self.caminho}",
                "versao": "1.0"
            },
            "clausulas": clausulas
        }

    def salvar_json(self, modelo: Dict, caminho_output: str):
        """
        Salva modelo em arquivo JSON.
        """
        with open(caminho_output, 'w', encoding='utf-8') as f:
            json.dump(modelo, f, ensure_ascii=False, indent=2)
```

## ✅ Checklist de Implementação

- [ ] Criar módulo `versiona-ai/importador_modelo.py` com classe `ImportadorModelo`
- [ ] Adicionar comando `importar-modelo` no `versiona_cli.py`
- [ ] Implementar validação de estrutura da planilha
- [ ] Implementar lógica de conversão XLSX → JSON
- [ ] Adicionar tratamento de erros e warnings
- [ ] Adicionar testes unitários para o importador
- [ ] Testar com planilha de exemplo: [Contrato SAP Serviços](./assets/contrato-sap-servicos/Contrato%20SAP%20Serviços%20-%20planilha.xlsx)
- [ ] Validar JSON gerado contra formato esperado: [modelo-contrato-importacao.json](./assets/contrato-sap-servicos/modelo-contrato-importacao.json)
- [ ] Documentar uso no README

## 📚 Referências

- **Planilha de Exemplo**: [Contrato SAP Serviços - planilha.xlsx](./assets/contrato-sap-servicos/Contrato%20SAP%20Serviços%20-%20planilha.xlsx)
- **JSON de Referência**: [modelo-contrato-importacao.json](./assets/contrato-sap-servicos/modelo-contrato-importacao.json)
- **CLI Principal**: `versiona_cli.py`

## 🔍 Critérios de Aceitação

1. ✅ Ferramenta CLI funcional com comando `importar-modelo`
2. ✅ Validação completa da estrutura da planilha
3. ✅ Geração de JSON no formato correto
4. ✅ Tratamento adequado de erros com mensagens claras
5. ✅ Modo `--validate-only` para verificação sem geração
6. ✅ Modo `--strict` para falhar em warnings
7. ✅ Testes com planilha de exemplo bem-sucedidos
