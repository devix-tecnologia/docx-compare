-- =================================================================
-- Schema básico do Directus para testes E2E UI
-- =================================================================
-- NOTA: Este script é PULADO se o backup foi restaurado (00-restore-backup.sh)
-- O backup já contém todas as tabelas Directus + customizações

-- Verificar se backup foi restaurado (se existem muitas tabelas Directus)
DO $$
DECLARE
    directus_tables_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO directus_tables_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name LIKE 'directus_%';
    
    IF directus_tables_count > 10 THEN
        RAISE NOTICE '⏭️  PULANDO 01-schema.sql - Backup já restaurado (% tabelas Directus encontradas)', directus_tables_count;
        RETURN; -- Sair do script
    END IF;
    
    RAISE NOTICE '📝 Executando 01-schema.sql - Criando schema manualmente';
END $$;

-- Tabela de modelos de contrato
CREATE TABLE IF NOT EXISTS modelo_contrato (
    id VARCHAR(255) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Tabela de cláusulas
CREATE TABLE IF NOT EXISTS clausula (
    id VARCHAR(255) PRIMARY KEY,
    modelo_contrato VARCHAR(255) REFERENCES modelo_contrato(id),
    referencia VARCHAR(50) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    conteudo TEXT,
    ordem INTEGER DEFAULT 0,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Tabela de versões de contrato
CREATE TABLE IF NOT EXISTS contrato_versao (
    id VARCHAR(255) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    modelo_contrato VARCHAR(255) REFERENCES modelo_contrato(id),
    arquivo VARCHAR(500),
    status VARCHAR(50) DEFAULT 'aguardando_processamento',
    criado_em TIMESTAMP DEFAULT NOW(),
    processado_em TIMESTAMP
);

-- Tabela de modificações
CREATE TABLE IF NOT EXISTS modificacao (
    id VARCHAR(255) PRIMARY KEY,
    versao VARCHAR(255) REFERENCES contrato_versao(id),
    clausula VARCHAR(255) REFERENCES clausula(id),  -- Task 010: FK para cláusula
    tipo VARCHAR(50) NOT NULL,
    conteudo_original TEXT,
    conteudo_modificado TEXT,
    ordem INTEGER DEFAULT 0,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_clausula_modelo ON clausula(modelo_contrato);
CREATE INDEX IF NOT EXISTS idx_versao_modelo ON contrato_versao(modelo_contrato);
CREATE INDEX IF NOT EXISTS idx_modificacao_versao ON modificacao(versao);
CREATE INDEX IF NOT EXISTS idx_modificacao_clausula ON modificacao(clausula);

-- Log de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Schema E2E UI criado/verificado com sucesso!';
END $$;
