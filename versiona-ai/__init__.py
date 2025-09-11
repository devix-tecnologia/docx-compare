"""
Versiona AI - Sistema de Versionamento Inteligente de Documentos

Sistema avançado de comparação e análise de diferenças entre documentos DOCX,
com foco em contratos e documentos jurídicos.

Principais características:
- Inversão de dependência com Protocols Python
- Integração com Directus CMS
- Implementações mock para testes rápidos
- Visualização web responsiva
- Pipeline funcional completo

Exemplo de uso básico:
    from versiona_ai.core.implementacoes_mock import FactoryImplementacoesMock
    from versiona_ai.core.pipeline_funcional import executar_pipeline_completo
    
    factory = FactoryImplementacoesMock()
    processador, analisador, comparador, agrupador = factory.criar_todos()
    
    resultados = executar_pipeline_completo(
        documentos_originais=[original_docx],
        documentos_modificados=[modificado_docx],
        modelos=[modelo_contrato],
        contexto=contexto,
        processador=processador,
        analisador=analisador,
        comparador=comparador,
        agrupador=agrupador
    )
"""

__version__ = "1.0.0"
__author__ = "Devix Tecnologia"
__description__ = "Sistema de Versionamento Inteligente de Documentos"

# Importações principais para facilitar o uso
try:
    from .core.pipeline_funcional import (
        executar_pipeline_completo,
        ProcessadorTexto,
        AnalisadorTags,
        ComparadorDocumentos,
        AgrupadorModificacoes,
    )
    from .core.implementacoes_mock import FactoryImplementacoesMock
    from .core.implementacoes_directus import (
        FactoryImplementacoes,
        ConfiguracaoDirectus,
    )
    
    __all__ = [
        "executar_pipeline_completo",
        "ProcessadorTexto",
        "AnalisadorTags", 
        "ComparadorDocumentos",
        "AgrupadorModificacoes",
        "FactoryImplementacoesMock",
        "FactoryImplementacoes",
        "ConfiguracaoDirectus",
    ]
    
except ImportError:
    # Importações podem falhar dependendo da configuração do PYTHONPATH
    # Em produção, isso deve ser configurado adequadamente
    __all__ = []
