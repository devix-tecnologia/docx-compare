#!/usr/bin/env python3
"""
Gerador de HTML com diff visual para documentos DOCX
Integra com o pipeline existente e gera visualização web responsiva
"""

import sys
import tempfile
from pathlib import Path
from typing import Any

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from docx_compare.core.implementacoes_mock import FactoryImplementacoesMock
from docx_compare.core.pipeline_funcional import (
    ContextoProcessamento,
    PrioridadeProcessamento,
    executar_pipeline_completo,
)
from docx_compare.core.teste_implementacoes_mock import criar_modelo_teste


def gerar_html_diff(
    caminho_original: Path,
    caminho_modificado: Path,
    titulo: str = "Comparação de Documentos",
    usar_mock: bool = True,
) -> str:
    """
    Gera HTML com visualização diff entre dois documentos.

    Args:
        caminho_original: Caminho do documento original
        caminho_modificado: Caminho do documento modificado
        titulo: Título da comparação
        usar_mock: Se deve usar implementações mock (True) ou reais (False)

    Returns:
        String contendo HTML completo
    """
    # Configurar implementações
    if usar_mock:
        factory = FactoryImplementacoesMock()
        processador, analisador, comparador, agrupador = factory.criar_todos()
    else:
        # Aqui você integraria com as implementações reais do Directus
        raise NotImplementedError(
            "Implementações reais do Directus ainda não configuradas"
        )

    # Executar pipeline
    modelos = [criar_modelo_teste()]
    contexto = ContextoProcessamento(
        prioridade=PrioridadeProcessamento.NORMAL,
        timeout_segundos=30,
        modo_paralelo=False,
        filtros_ativos=set(),
        configuracoes={},
    )

    resultados = executar_pipeline_completo(
        documentos_originais=[caminho_original],
        documentos_modificados=[caminho_modificado],
        _modelos=modelos,
        _contexto=contexto,
        processador=processador,
        analisador=analisador,
        comparador=comparador,
        agrupador=agrupador,
    )

    # Ler conteúdo dos arquivos
    with open(caminho_original, encoding="utf-8") as f:
        conteudo_original = f.read()

    with open(caminho_modificado, encoding="utf-8") as f:
        conteudo_modificado = f.read()

    # Gerar HTML
    resultado = resultados[0]
    html = gerar_template_html(
        titulo=titulo,
        conteudo_original=conteudo_original,
        conteudo_modificado=conteudo_modificado,
        modificacoes=resultado.modificacoes,
        blocos=resultado.blocos_agrupados,
        estatisticas=resultado,
    )

    return html


def gerar_template_html(
    titulo: str,
    conteudo_original: str,
    conteudo_modificado: str,
    modificacoes: list[Any],
    blocos: list[Any],
    estatisticas: Any,
) -> str:
    """
    Gera template HTML completo com CSS e JavaScript embutidos.
    """
    # Processar modificações para highlight
    modificacoes_js = []
    for mod in modificacoes:
        modificacoes_js.append(
            {
                "id": mod.id,
                "tipo": mod.tipo.value,
                "original": str(mod.conteudo_original),
                "novo": str(mod.conteudo_novo),
                "linha": mod.posicao_original.linha,
                "coluna": mod.posicao_original.coluna,
                "confianca": mod.confianca,
                "tags": list(mod.tags_relacionadas),
            }
        )

    html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .stat-item {{
            background: #e9ecef;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }}

        .diff-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .document-panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .panel-header {{
            background: #495057;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }}

        .panel-content {{
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.8;
            white-space: pre-wrap;
        }}

        .modifications-panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .modification-item {{
            border-bottom: 1px solid #e9ecef;
            padding: 15px 20px;
        }}

        .modification-item:last-child {{
            border-bottom: none;
        }}

        .mod-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .mod-type {{
            background: #007bff;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            text-transform: uppercase;
        }}

        .mod-type.alteracao {{ background: #dc3545; }}
        .mod-type.insercao {{ background: #28a745; }}
        .mod-type.remocao {{ background: #fd7e14; }}

        .mod-confidence {{
            color: #6c757d;
            font-size: 14px;
        }}

        .mod-content {{
            font-family: 'Courier New', monospace;
            margin-bottom: 8px;
        }}

        .mod-original {{
            background: #f8d7da;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 10px;
        }}

        .mod-new {{
            background: #d4edda;
            padding: 2px 6px;
            border-radius: 3px;
        }}

        .mod-position {{
            font-size: 12px;
            color: #6c757d;
        }}

        .highlight {{
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }}

        .highlight-alteracao {{
            background-color: #ffe6e6;
            border-left: 3px solid #dc3545;
        }}

        .highlight-insercao {{
            background-color: #e6ffe6;
            border-left: 3px solid #28a745;
        }}

        .highlight-remocao {{
            background-color: #fff4e6;
            border-left: 3px solid #fd7e14;
        }}

        .confidence-high {{ border-left-width: 4px; }}
        .confidence-medium {{ border-left-width: 3px; }}
        .confidence-low {{ border-left-width: 2px; }}

        .legend {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .legend-items {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}

        @media (max-width: 768px) {{
            .diff-container {{
                grid-template-columns: 1fr;
            }}

            .stats {{
                flex-direction: column;
            }}

            .legend-items {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{titulo}</h1>
            <div class="stats">
                <div class="stat-item">📊 {len(modificacoes)} modificações encontradas</div>
                <div class="stat-item">📦 {len(blocos)} blocos agrupados</div>
                <div class="stat-item">⏱️ {estatisticas.tempo_processamento:.3f}s processamento</div>
                <div class="stat-item">🎯 Confiança média: {sum(m.confianca for m in modificacoes) / len(modificacoes) * 100:.1f}%</div>
            </div>
        </div>

        <div class="diff-container">
            <div class="document-panel">
                <div class="panel-header">📄 Documento Original</div>
                <div class="panel-content" id="original-content">{conteudo_original}</div>
            </div>

            <div class="document-panel">
                <div class="panel-header">📝 Documento Modificado</div>
                <div class="panel-content" id="modified-content">{conteudo_modificado}</div>
            </div>
        </div>

        <div class="modifications-panel">
            <div class="panel-header">🔍 Modificações Detalhadas</div>
            {"".join(gerar_html_modificacao(mod) for mod in modificacoes)}
        </div>

        <div class="legend">
            <h3>📋 Legenda</h3>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffe6e6; border-left: 3px solid #dc3545;"></div>
                    <span>Alteração</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #e6ffe6; border-left: 3px solid #28a745;"></div>
                    <span>Inserção</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #fff4e6; border-left: 3px solid #fd7e14;"></div>
                    <span>Remoção</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Dados das modificações (gerados pelo Python)
        const modificacoes = {str(modificacoes_js).replace("'", '"')};

        // Aplicar highlights aos documentos
        function aplicarHighlights() {{
            // Esta função poderia aplicar highlights baseados nas posições
            // Por simplicidade, estamos mostrando as modificações em lista separada
            console.log('Modificações carregadas:', modificacoes.length);
        }}

        // Executar ao carregar a página
        document.addEventListener('DOMContentLoaded', aplicarHighlights);
    </script>
</body>
</html>
"""

    return html_template


def gerar_html_modificacao(mod: Any) -> str:
    """
    Gera HTML para uma modificação individual.
    """
    confidence_class = (
        "high" if mod.confianca >= 0.9 else "medium" if mod.confianca >= 0.7 else "low"
    )

    return f"""
    <div class="modification-item">
        <div class="mod-header">
            <span class="mod-type {mod.tipo.value}">{mod.tipo.value}</span>
            <span class="mod-confidence">{mod.confianca * 100:.0f}% confiança</span>
        </div>
        <div class="mod-content">
            <span class="mod-original">"{mod.conteudo_original}"</span>
            →
            <span class="mod-new">"{mod.conteudo_novo}"</span>
        </div>
        <div class="mod-position">
            Linha {mod.posicao_original.linha}, Coluna {mod.posicao_original.coluna}
            {f"• Tags: {', '.join(mod.tags_relacionadas)}" if mod.tags_relacionadas else ""}
        </div>
    </div>
    """


def exemplo_uso():
    """
    Demonstra como usar o gerador de HTML diff.
    """
    print("🌐 Gerador de HTML Diff para Documentos")
    print("=" * 50)

    # Criar arquivos temporários para demonstração
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_original.txt", delete=False
    ) as f1:
        conteudo_original = """CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: {{nome_contratante}}
CONTRATADA: {{nome_contratada}}

CLÁUSULA 1ª - OBJETO
O objeto do presente contrato é a prestação de {{tipo_servico}}.

CLÁUSULA 2ª - VALOR
O valor total dos serviços é de R$ {{valor}} reais.

CLÁUSULA 3ª - PRAZO
Os serviços deverão ser executados em {{prazo}} dias úteis.

CLÁUSULA 4ª - PAGAMENTO
O pagamento será efetuado mediante {{forma_pagamento}}.

Data: {{data_contrato}}"""
        f1.write(conteudo_original)
        caminho_original = Path(f1.name)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_modificado.txt", delete=False
    ) as f2:
        conteudo_modificado = """CONTRATO DE PRESTAÇÃO DE SERVIÇOS ESPECIALIZADOS

CONTRATANTE: {{nome_contratante}}
CONTRATADA: {{nome_contratada}}

CLÁUSULA 1ª - OBJETO
O objeto do presente contrato é a prestação de {{tipo_servico}}.

CLÁUSULA 2ª - VALOR
O valor total dos serviços é de R$ {{preco}} reais.

CLÁUSULA 3ª - PRAZO
Os serviços deverão ser executados em {{prazo}} dias corridos.

CLÁUSULA 4ª - PAGAMENTO
O pagamento será efetuado mediante {{forma_pagamento}}.

CLÁUSULA 5ª - REAJUSTE
Os valores serão reajustados conforme {{indice_reajuste}}.

Data: {{data_contrato}}"""
        f2.write(conteudo_modificado)
        caminho_modificado = Path(f2.name)

    try:
        # Gerar HTML diff
        html_resultado = gerar_html_diff(
            caminho_original=caminho_original,
            caminho_modificado=caminho_modificado,
            titulo="Comparação de Contrato - Original vs Modificado",
            usar_mock=True,
        )

        # Salvar HTML
        output_path = Path(__file__).parent / "exemplo_diff.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_resultado)

        print(f"✅ HTML diff gerado em: {output_path}")
        print(f"📄 Arquivo de {len(html_resultado)} caracteres")
        print("🌐 Abra o arquivo HTML em um navegador para visualizar")

        return output_path

    finally:
        # Limpar arquivos temporários
        caminho_original.unlink()
        caminho_modificado.unlink()


if __name__ == "__main__":
    exemplo_uso()
