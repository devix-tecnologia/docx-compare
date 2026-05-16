-- =================================================================
-- Usuários de teste para E2E UI
-- =================================================================
-- NOTA: Este script é PULADO se o backup foi restaurado (00-restore-backup.sh)
-- O backup já contém a role Public e configurações de usuário
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
        RAISE NOTICE '⏭️  PULANDO 03-usuarios.sql - Backup já restaurado';
        RETURN;
    END IF;

    RAISE NOTICE '📝 Executando 03-usuarios.sql - Configurando usuários';
END $$;

-- =================================================================
-- 1. CRIAR ROLE PÚBLICA
-- =================================================================
-- Role pública necessária para acesso não autenticado aos endpoints
-- UUID padrão do Directus: 00000000-0000-0000-0000-000000000000

INSERT INTO directus_roles (
    id,
    name,
    icon,
    description,
    admin_access,
    app_access
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    'Public',
    'public',
    'Public role for unauthenticated access',
    false,
    false
) ON CONFLICT (id) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE '✅ Role Public criada com UUID: 00000000-0000-0000-0000-000000000000';
END $$;

-- =================================================================
-- 2. USUÁRIO ADMIN
-- =================================================================
-- Cria usuário admin de teste se ainda não existir

-- Nota: Directus já cria o admin inicial via env vars
-- Este script é backup caso seja necessário criar via SQL

DO $$
BEGIN
    -- Apenas log, usuário é criado pelo Directus automaticamente
    RAISE NOTICE '✅ Usuário admin será criado pelo Directus via env vars';
    RAISE NOTICE '    Email: admin@example.com';
    RAISE NOTICE '    Password: TestPassword123!';
END $$;
