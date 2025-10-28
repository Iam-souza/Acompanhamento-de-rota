# Acompanhamento de Rotas

Pequeno guia: como testar o trigger de criação de perfis

1) Defina variáveis de ambiente (local):

```bash
export SUPABASE_URL="https://juztvqedchxluixbrzfg.supabase.co"
export SUPABASE_KEY="<eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1enR2cWVkY2h4bHVpeGJyemZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMDUwNjEsImV4cCI6MjA3Njg4MTA2MX0.9XTz8UsLvEV-zJloDMSvM54AhLobmB5HETynKA7wCyc>"
# opcional, para leitura/admin:
export SUPABASE_SERVICE_KEY="<eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1enR2cWVkY2h4bHVpeGJyemZnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwNTA2MSwiZXhwIjoyMDc2ODgxMDYxfQ.RqbV_r-UEzrRPsRep3eEIcDVHaKDYOYA3kDGIChyCLY>"
```

2) Instale dependências e rode o script de teste:

```bash
pip install -r requirements.txt
python scripts/test_signup.py
```

3) Resultado: o script tentará criar um usuário via supabase.auth.sign_up e então buscar o perfil em `public.app_0c87e04f3a_usuarios`.

Se quiser que o app Streamlit use automaticamente Supabase Auth para registrar e confiar no trigger, eu já atualizei `auth.py` para preferir `client.auth.sign_up(...)` e usar o trigger para criação do perfil.
