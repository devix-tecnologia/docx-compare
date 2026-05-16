-- =================================================================
-- Seed de dados para testes E2E UI - Task 011
-- =================================================================
-- NOTA: Este script é PULADO se o backup foi restaurado (00-restore-backup.sh)
-- O backup já contém todos os dados de teste
-- =================================================================

-- Verificar se backup foi restaurado
DO $$
DECLARE
    directus_tables_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO directus_tables_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name LIKE 'directus_%';

    IF directus_tables_count > 10 THEN
        RAISE NOTICE '⏭️  PULANDO 02-modelo-contrato.sql - Backup já restaurado';
        RETURN;
    END IF;

    RAISE NOTICE '📝 Executando 02-modelo-contrato.sql - Inserindo dados de teste';
END $$;

-- Inserir modelo de contrato de teste
INSERT INTO modelo_contrato (id, nome, descricao, ativo, criado_em)
VALUES (
    'e2e-modelo-001',
    'Modelo Teste Task 010',
    'Modelo de contrato para validação E2E de vinculação cláusulas-modificações',
    true,
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Inserir cláusulas típicas do modelo
INSERT INTO clausula (id, modelo_contrato, referencia, nome, conteudo, ordem, criado_em)
VALUES
    (
        'e2e-clausula-001',
        'e2e-modelo-001',
        '1.0',
        'Das Partes',
        'Este contrato é celebrado entre as partes qualificadas no preâmbulo.',
        1,
        NOW()
    ),
    (
        'e2e-clausula-002',
        'e2e-modelo-001',
        '2.0',
        'Do Objeto',
        'O objeto do presente contrato consiste na prestação de serviços conforme especificado.',
        2,
        NOW()
    ),
    (
        'e2e-clausula-003',
        'e2e-modelo-001',
        '3.0',
        'Do Prazo',
        'O prazo de vigência deste contrato será de 12 (doze) meses.',
        3,
        NOW()
    ),
    (
        'e2e-clausula-004',
        'e2e-modelo-001',
        '4.0',
        'Do Valor',
        'O valor total dos serviços será de R$ 10.000,00 (dez mil reais).',
        4,
        NOW()
    ),
    (
        'e2e-clausula-005',
        'e2e-modelo-001',
        '5.0',
        'Das Obrigações do Contratante',
        'O contratante obriga-se a fornecer todas as informações necessárias.',
        5,
        NOW()
    ),
    (
        'e2e-clausula-006',
        'e2e-modelo-001',
        '6.0',
        'Das Obrigações do Contratado',
        'O contratado obriga-se a executar os serviços com qualidade.',
        6,
        NOW()
    ),
    (
        'e2e-clausula-007',
        'e2e-modelo-001',
        '7.0',
        'Da Rescisão',
        'Este contrato poderá ser rescindido mediante notificação prévia de 30 dias.',
        7,
        NOW()
    ),
    (
        'e2e-clausula-008',
        'e2e-modelo-001',
        '8.0',
        'Das Penalidades',
        'O descumprimento das obrigações sujeitará a parte infratora a multa.',
        8,
        NOW()
    ),
    (
        'e2e-clausula-009',
        'e2e-modelo-001',
        '9.0',
        'Do Foro',
        'Fica eleito o foro da comarca da capital para dirimir questões.',
        9,
        NOW()
    ),
    (
        'e2e-clausula-010',
        'e2e-modelo-001',
        '10.0',
        'Disposições Gerais',
        'As partes declaram estar cientes e de acordo com todas as cláusulas.',
        10,
        NOW()
    )
ON CONFLICT (id) DO NOTHING;

-- Inserir versão de teste já processada (para testes rápidos)
INSERT INTO contrato_versao (id, nome, modelo_contrato, status, criado_em, processado_em)
VALUES (
    'e2e-versao-001',
    'Versão Teste E2E - Pré-processada',
    'e2e-modelo-001',
    'concluido',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Inserir modificações de exemplo vinculadas às cláusulas (Task 010)
INSERT INTO modificacao (id, versao, clausula, tipo, conteudo_original, conteudo_modificado, ordem, criado_em)
VALUES
    (
        'e2e-mod-001',
        'e2e-versao-001',
        'e2e-clausula-003',  -- Vinculado à cláusula "Do Prazo"
        'alteracao',
        'O prazo de vigência deste contrato será de 12 (doze) meses.',
        'O prazo de vigência deste contrato será de 24 (vinte e quatro) meses.',
        1,
        NOW()
    ),
    (
        'e2e-mod-002',
        'e2e-versao-001',
        'e2e-clausula-004',  -- Vinculado à cláusula "Do Valor"
        'alteracao',
        'O valor total dos serviços será de R$ 10.000,00 (dez mil reais).',
        'O valor total dos serviços será de R$ 15.000,00 (quinze mil reais).',
        2,
        NOW()
    ),
    (
        'e2e-mod-003',
        'e2e-versao-001',
        'e2e-clausula-007',  -- Vinculado à cláusula "Da Rescisão"
        'remocao',
        'Este contrato poderá ser rescindido mediante notificação prévia de 30 dias.',
        '',
        3,
        NOW()
    ),
    (
        'e2e-mod-004',
        'e2e-versao-001',
        'e2e-clausula-005',  -- Vinculado à cláusula "Das Obrigações do Contratante"
        'insercao',
        '',
        'O contratante também deverá fornecer acesso aos sistemas corporativos.',
        4,
        NOW()
    )
ON CONFLICT (id) DO NOTHING;

-- Log de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Seed E2E UI aplicado com sucesso!';
    RAISE NOTICE '   - 1 modelo de contrato';
    RAISE NOTICE '   - 10 cláusulas';
    RAISE NOTICE '   - 1 versão processada';
    RAISE NOTICE '   - 4 modificações vinculadas (Task 010)';
END $$;
