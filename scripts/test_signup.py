"""
Teste rápido para criar um usuário via Supabase Auth e verificar se o trigger criou o perfil

Uso:
  1) Instale dependências (uma vez):
     pip install -r requirements.txt

  2) Exporte variáveis de ambiente (substituir pelos seus valores):
     export SUPABASE_URL="https://<SEU_PROJECT>.supabase.co"
     export SUPABASE_KEY="<ANON_KEY>"

  3) Rode o script:
     python scripts/test_signup.py

O script cria um usuário com email aleatório (teste) e então tenta buscar o perfil
na tabela `public.app_0c87e04f3a_usuarios`. Ele não usa a service_role key;
se a política RLS bloquear a leitura, você pode fornecer uma service_role key
via SUPABASE_SERVICE_KEY para a verificação.

Observação: este script é para testes locais. Não use em produção com dados reais.
"""

import os
import time
import uuid
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Defina SUPABASE_URL e SUPABASE_KEY como variáveis de ambiente antes de rodar.")
    exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)
admin = None
if SERVICE_KEY:
    admin = create_client(SUPABASE_URL, SERVICE_KEY)

# Gera um email de teste único
unique = str(uuid.uuid4())[:8]
email = f"teste+{unique}@example.com"
password = "SenhaForte123!"

print(f"Criando usuário de teste: {email}")

# Tenta sign_up via Auth
try:
    # tentar assinatura com a forma mais compatível
    try:
        resp = client.auth.sign_up({"email": email, "password": password})
    except Exception:
        resp = client.auth.sign_up(email=email, password=password)
    print("Resposta do sign_up:", resp)
except Exception as e:
    print("Erro ao chamar supabase.auth.sign_up:", e)
    print("Abortando teste.")
    exit(1)

# aguarda alguns segundos para o trigger rodar
print("Aguardando 3 segundos para o trigger criar o perfil...")
time.sleep(3)

# Usa admin client se disponível para garantir leitura mesmo com RLS
db_client = admin if admin else client

query = db_client.table('app_0c87e04f3a_usuarios').select('*').eq('email', email).execute()
print('Resultado da busca por perfil:', query)

if query.data:
    print('Perfil criado com sucesso!')
else:
    print('Perfil NÃO encontrado. Verifique:')
    print('- trigger foi criado?')
    print('- a função executou sem erros (ver logs DB)?')
    print('- se RLS bloqueou a leitura, tente fornecer SUPABASE_SERVICE_KEY e reexecute.')
