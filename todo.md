Sistema de Acompanhamento de Rotas - MVP Todo List
Arquivos a serem criados:
app.py - Aplicação principal Streamlit

Sistema de login/autenticação
Interface principal com upload, filtros, tabela editável
Gerenciamento de sessão
database.py - Configuração e operações do Supabase

Conexão com Supabase
Funções CRUD para todas as tabelas
Funções de consolidação de dados
auth.py - Sistema de autenticação

Hash de senhas com bcrypt
Validação de login
Gerenciamento de sessão
utils.py - Funções utilitárias

Processamento de arquivos CSV/Excel
Funções de exportação
Validações de dados
requirements.txt - Dependências do projeto

Estrutura do Banco (Supabase):
Tabela: app_0c87e04f3a_relatorios_raw (dados brutos do upload)
Tabela: app_0c87e04f3a_relatorios_consolidados (dados consolidados editáveis)
Tabela: app_0c87e04f3a_usuarios (controle de acesso)
Funcionalidades principais:
✅ Login seguro com bcrypt
✅ Upload CSV/Excel com pré-visualização
✅ Consolidação automática de dados
✅ Tabela editável com dropdowns específicos
✅ Filtros em tempo real
✅ Exportação de dados filtrados
✅ Interface responsiva e limpa
Campos editáveis com dropdowns:
log: 1-10
certidao: Sim/Não
ativo: Com sucesso/Sem sucesso
tratativa: Resolvido/Não resolvido
responsavel: CARLOS, CINDI, EDILENE, EDUARDA, IGOR, MARCELO, THIAGO