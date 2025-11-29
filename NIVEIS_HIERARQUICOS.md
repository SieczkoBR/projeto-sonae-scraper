# SISTEMA DE NÍVEIS HIERÁRQUICOS - McSonae Dashboard

## Cálculo Automático de Níveis

O sistema de níveis hierárquicos é calculado automaticamente baseado na quantidade de permissões que cada cargo possui.

### Fórmula
```
Pontos por permissão = 100 ÷ Total de permissões
Nível do cargo = Quantidade de permissões do cargo × Pontos por permissão
```

### Exceção
- **Admin sempre = 100** (independente do número de permissões)

### Exemplo Atual (15 permissões totais)
```
100 ÷ 15 = 6.67 pontos por permissão

1. Admin:         15 permissões × 6.67 = 100 (exceção - fixo em 100)
2. Desenvolvedor: 11 permissões × 6.67 = 73
3. Gestor:        11 permissões × 6.67 = 73
4. Analista:       8 permissões × 6.67 = 53
5. Visualizador:   4 permissões × 6.67 = 27
```

## Quando Atualizar os Níveis

Os níveis hierárquicos devem ser recalculados e atualizados no banco de dados sempre que:

1. **Uma nova permissão for adicionada** ao sistema
2. **Uma permissão for removida** do sistema
3. **Um cargo ganhar ou perder permissões**

### Como Atualizar

1. **Contar o total de permissões:**
   ```sql
   SELECT COUNT(*) FROM permissoes;
   ```

2. **Calcular pontos por permissão:**
   ```
   100 ÷ total_de_permissoes
   ```

3. **Para cada cargo (exceto admin):**
   - Contar quantas permissões o cargo tem
   - Multiplicar pela pontuação por permissão
   - Arredondar o resultado
   - Atualizar no banco:
     ```sql
     UPDATE cargos SET nivel_hierarquia = [valor_calculado] WHERE codigo = 'cargo_name';
     ```

4. **Admin sempre fica em 100:**
   ```sql
   UPDATE cargos SET nivel_hierarquia = 100 WHERE codigo = 'admin';
   ```

## Scripts de Manutenção

- **criar_cargo_dev.py**: Cria o cargo desenvolvedor e atualiza níveis
- **atualizar_cargos.py**: Redefine todos os cargos e recalcula níveis

Execute esses scripts após modificar permissões no sistema.

## Estrutura Atual (29/11/2025)

**Total de Permissões:** 15

### Permissões do Sistema
1. view_dashboard - Visualizar Dashboard
2. view_projects - Visualizar Projetos
3. view_reports - Visualizar Relatórios
4. view_ai_insights - Visualizar Insights IA
5. create_reports - Criar Relatórios
6. edit_projects - Editar Projetos
7. delete_projects - Deletar Projetos
8. delete_reports - Deletar Relatórios
9. upload_files - Upload de Arquivos
10. import_data - Importar Dados
11. view_logs - Visualizar Logs
12. approve_accounts - Aprovar Contas (Admin)
13. manage_users - Gerenciar Usuários (Admin)
14. manage_permissions - Gerenciar Permissões (Admin)
15. system_config - Configurar Sistema (Admin)

### Distribuição por Cargo

**Admin (100):** Todas as 15 permissões

**Desenvolvedor (73):** 11 permissões
- view_dashboard, view_projects, view_reports, view_ai_insights
- create_reports, edit_projects, delete_projects, delete_reports
- upload_files, import_data, view_logs

**Gestor (73):** 11 permissões
- view_dashboard, view_projects, view_reports, view_ai_insights
- create_reports, edit_projects, delete_projects, delete_reports
- upload_files, import_data, view_logs

**Analista (53):** 8 permissões
- view_dashboard, view_projects, view_reports, view_ai_insights
- create_reports, edit_projects, upload_files, import_data

**Visualizador (27):** 4 permissões
- view_dashboard, view_projects, view_reports, view_ai_insights
