# Acompanhamento de Rotas

Pequeno guia: como testar o trigger de criação de perfis

1) Defina variáveis de ambiente (local):

```bash
# Defina suas variáveis de ambiente em um arquivo .env seguro ou exporte na sessão.
# NUNCA coloque chaves reais em arquivos públicos (README, gist, etc.).
export SUPABASE_URL="https://<SEU_PROJECT>.supabase.co"
export SUPABASE_KEY="<SUA_ANON_KEY>"
# opcional (recomendado para leitura/admin):
export SUPABASE_SERVICE_KEY="<SUA_SERVICE_ROLE_KEY>"
```

2) Instale dependências e rode o script de teste:

```bash
pip install -r requirements.txt
python scripts/test_signup.py
```

3) Resultado: o script tentará criar um usuário via supabase.auth.sign_up e então buscar o perfil em `public.app_0c87e04f3a_usuarios`.

Se quiser que o app Streamlit use automaticamente Supabase Auth para registrar e confiar no trigger, eu já atualizei `auth.py` para preferir `client.auth.sign_up(...)` e usar o trigger para criação do perfil.
