# Task 008: Adicionar Status Intermediário "processando" Durante Processamento

Status: pending

## Descrição

Atualmente, enquanto uma versão está sendo processada, ela permanece com `status = "processar"` até a conclusão, quando muda diretamente para `"concluido"` ou `"erro"`.

### Fluxo Atual:

```
"processar" → [Processamento ocorre silenciosamente] → "concluido" | "erro"
```

**Problemas:**

1. ❌ **Impossível distinguir** versões aguardando vs em processamento ativo
2. ❌ **Usuário não tem feedback** de que o processamento iniciou
3. ❌ **Risco de reprocessamento** se sistema reiniciar durante processamento
4. ❌ **Sem visibilidade** de versões travadas em processamento

### Exemplo Real:

- Versão criada com `status = "processar"` às 14:00
- Processamento inicia às 14:05 (status continua "processar")
- Processamento termina às 14:10 (status muda para "concluido")
- **Durante 5 minutos:** impossível saber se está processando ou aguardando

---

## 🎯 Solução

Adicionar atualização de status para `"processando"` ou `"em_processamento"` no **início** do processamento.

### Fluxo Proposto:

```
"processar" → "processando" → "concluido" | "erro"
```

**Benefícios:**

1. ✅ Visibilidade clara do estado da versão
2. ✅ Possibilidade de retry automático se travar
3. ✅ Melhor UX no frontend (loading states)
4. ✅ Métricas de tempo de processamento mais precisas
5. ✅ Evita reprocessamento duplicado

---

## 📍 Componentes Afetados

### 1. Repository (`versiona-ai/repositorio.py`)

**Adicionar método:**

```python
def atualizar_status_versao(
    self,
    versao_id: str,
    status: str,
    observacao: str | None = None
) -> dict[str, Any]:
    """
    Atualiza apenas o status de uma versão.

    Args:
        versao_id: ID da versão
        status: Novo status ("processar", "processando", "concluido", "erro")
        observacao: Observação opcional

    Returns:
        dict com success, status_code, data, error
    """
    update_data = {"status": status}

    if observacao:
        update_data["observacao"] = observacao

    return self.update_versao(versao_id, update_data, timeout=10)
```

### 2. Processador Automático (`src/docx_compare/processors/processador_automatico.py`)

**Atualizar fluxo de processamento:**

```python
def processar_versao(versao):
    """Processa uma versão"""
    versao_id = versao.get("id")

    try:
        # 1. NOVO: Atualizar para "processando" no início
        print(f"🔄 Atualizando status para 'processando'...")
        repo.atualizar_status_versao(
            versao_id,
            status="processando",
            observacao=f"Processamento iniciado em {datetime.now().isoformat()}"
        )

        # 2. Download de arquivos
        original = download_arquivo(...)
        modificado = download_arquivo(...)

        # 3. Processar comparação
        resultado = processar_comparacao(original, modificado)

        # 4. Persistir resultados com status "concluido"
        repo.registrar_resultado_processamento_versao(
            versao_id=versao_id,
            modificacoes=resultado.modificacoes,
            status="concluido"  # ← Status final
        )

    except Exception as e:
        # 5. Em caso de erro, atualizar para "erro"
        repo.atualizar_status_versao(
            versao_id,
            status="erro",
            observacao=f"Erro: {str(e)}"
        )
```

### 3. DirectusAPI (`versiona-ai/directus_server.py`)

**Atualizar `process_versao` e `_process_versao_com_ast`:**

```python
def process_versao(self, versao_id, mock=False, use_ast=True):
    """Processa uma versão específica"""

    try:
        # NOVO: Atualizar status no início
        if not mock:
            print(f"🔄 Atualizando status da versão {versao_id} para 'processando'")
            self.repo.atualizar_status_versao(
                versao_id,
                status="processando",
                observacao=f"Processamento iniciado via API em {datetime.now().isoformat()}"
            )

        # Buscar dados da versão
        versao_data = self.repo.get_versao_para_processar(versao_id)

        # Processar com AST
        if use_ast:
            resultado = self._process_versao_com_ast(versao_id, versao_data)
        else:
            resultado = self._process_versao_texto_plano(versao_id, versao_data)

        # Status "concluido" é setado por registrar_resultado_processamento_versao
        return resultado

    except Exception as e:
        # Erro: atualizar status
        if not mock:
            self.repo.atualizar_status_versao(
                versao_id,
                status="erro",
                observacao=f"Erro no processamento: {str(e)[:500]}"
            )
        raise
```

### 4. Orquestrador (`src/docx_compare/processors/orquestrador.py`)

**O orquestrador não precisa de alteração** - ele apenas detecta versões com `status = "processar"` e delega para os processadores.

---

## 🧪 Validação

### Teste Manual

```bash
# 1. Criar versão com status "processar"
curl -X POST "https://contract.devix.co/items/versao" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "processar", "contrato": "...", "arquivo": "..."}'

# 2. Processar versão
curl "http://localhost:5005/api/versoes/VERSAO_ID"

# 3. Durante processamento, consultar status
curl "https://contract.devix.co/items/versao/VERSAO_ID?fields=status,observacao" \
  -H "Authorization: Bearer $TOKEN"

# Esperado:
# - Antes: {"status": "processar"}
# - Durante: {"status": "processando", "observacao": "Processamento iniciado..."}
# - Depois: {"status": "concluido"}
```

### Teste Automatizado

```python
def test_status_muda_para_processando_no_inicio():
    """Status deve mudar para 'processando' antes de processar"""

    # Arrange
    versao_id = "test-versao-123"
    mock_repo = Mock()
    processor = DirectusAPI(mock_repo)

    # Act
    processor.process_versao(versao_id, mock=False)

    # Assert
    # Verificar que atualizar_status_versao foi chamado com "processando"
    mock_repo.atualizar_status_versao.assert_called_once_with(
        versao_id,
        status="processando",
        observacao=ANY
    )

def test_status_muda_para_erro_em_caso_de_falha():
    """Status deve mudar para 'erro' se processamento falhar"""

    # Arrange
    versao_id = "test-versao-123"
    mock_repo = Mock()
    mock_repo.get_versao_para_processar.side_effect = Exception("Erro simulado")
    processor = DirectusAPI(mock_repo)

    # Act & Assert
    with pytest.raises(Exception):
        processor.process_versao(versao_id, mock=False)

    # Verificar que status foi atualizado para "erro"
    calls = mock_repo.atualizar_status_versao.call_args_list
    assert any(call[1]["status"] == "erro" for call in calls)
```

---

## 📊 Impacto

### Backend

- ✅ **Baixo impacto**: Adiciona apenas 1 requisição HTTP extra por versão processada
- ✅ **Performance**: < 100ms de overhead (PATCH no Directus)
- ✅ **Compatibilidade**: Não quebra código existente

### Frontend

- ✅ **Melhoria de UX**: Pode exibir loading state real
- ✅ **Polling otimizado**: Pode verificar apenas versões "processando"
- ✅ **Feedback visual**: "Processando..." vs "Aguardando processamento"

### Monitoramento

- ✅ **Alertas**: Detectar versões travadas em "processando" há muito tempo
- ✅ **Métricas**: Tempo médio de processamento mais preciso
- ✅ **Debugging**: Saber exatamente quando processamento iniciou

---

## 🔄 Estratégia de Implementação

### Fase 1: Repository (15 min)

1. Adicionar método `atualizar_status_versao` em `repositorio.py`
2. Testar manualmente com curl

### Fase 2: DirectusAPI (30 min)

1. Atualizar `process_versao` para setar "processando"
2. Atualizar `_process_versao_com_ast` com tratamento de erro
3. Testar com versões reais

### Fase 3: Processador Automático (20 min)

1. Atualizar `processar_versao` no processador automático
2. Garantir que erros setam status "erro"
3. Testar em modo dry-run

### Fase 4: Validação (15 min)

1. Processar 5-10 versões em produção
2. Verificar logs de transição de status
3. Confirmar que nenhuma versão fica travada

**Tempo total estimado:** ~1.5 horas

---

## ⚠️ Considerações

### Versões Travadas em Processamento

**Problema:** E se processo morre durante processamento?

**Solução:** Implementar job de limpeza:

```python
# Script: scripts/limpar_status_travados.py
def limpar_status_travados():
    """Reseta versões travadas em 'processando' há mais de 1 hora"""

    # Buscar versões processando há muito tempo
    versoes = repo.get_versoes_por_status(
        status="processando",
        older_than="1 hour"
    )

    for versao in versoes:
        print(f"⚠️  Resetando versão {versao['id']} (travada há {tempo})")
        repo.atualizar_status_versao(
            versao["id"],
            status="processar",  # Volta para fila
            observacao="Status resetado automaticamente - processamento travado"
        )
```

### Modo Dry-Run

No modo `--dry-run`, **não atualizar status**:

```python
if not dry_run:
    repo.atualizar_status_versao(versao_id, "processando")
```

---

## 📝 Checklist de Implementação

- [ ] Adicionar `atualizar_status_versao` em `repositorio.py`
- [ ] Atualizar `DirectusAPI.process_versao` para setar "processando"
- [ ] Atualizar `DirectusAPI._process_versao_com_ast` com try/except
- [ ] Atualizar processador automático
- [ ] Respeitar modo `--dry-run` (não atualizar status)
- [ ] Adicionar testes unitários
- [ ] Testar manualmente em desenvolvimento
- [ ] Documentar em `docs/ARQUITETURA_E_FLUXO.md`
- [ ] Deploy em produção
- [ ] Monitorar primeiras 50 versões processadas
- [ ] Criar script de limpeza de status travados

---

## 🔗 Referências

- [docs/ARQUITETURA_E_FLUXO.md](../docs/ARQUITETURA_E_FLUXO.md) - Documentação atual do fluxo
- [versiona-ai/repositorio.py](../versiona-ai/repositorio.py) - Repository Pattern
- [versiona-ai/directus_server.py](../versiona-ai/directus_server.py) - DirectusAPI
- Task 007 - Exemplo de task concluída com sucesso

---

## 📅 Timeline

- **Criação:** 2026-03-02
- **Início:** TBD
- **Conclusão:** TBD

---

## 👤 Responsável

TBD
