# 🔐 Tutorial Completo: Configuração de Credenciais

Guia passo a passo para configurar todas as credenciais necessárias para o LinkedIn Content Generator.

---

## 📋 Índice

1. [Google Sheets - Service Account](#1-google-sheets-service-account)
2. [LinkedIn API - OAuth2 Token](#2-linkedin-api-oauth2-token)
3. [Configurar Credenciais no Kestra](#3-configurar-no-kestra)
4. [Verificar Configuração](#4-verificar-configuração)

---

## 1. Google Sheets - Service Account

### Passo 1.1: Criar Projeto no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Clique em **"Select a project"** no topo da página
3. Clique em **"NEW PROJECT"**
4. Configure:
   - **Project name**: `linkedin-automation` (ou nome de sua preferência)
   - **Organization**: Deixe como está
5. Clique em **"CREATE"**
6. Aguarde a criação (20-30 segundos)

### Passo 1.2: Ativar Google Sheets API

1. No menu lateral, vá em **"APIs & Services"** → **"Library"**
2. Na barra de busca, digite: `Google Sheets API`
3. Clique no resultado **"Google Sheets API"**
4. Clique em **"ENABLE"**
5. Aguarde a ativação

### Passo 1.3: Criar Service Account

1. No menu lateral, vá em **"APIs & Services"** → **"Credentials"**
2. Clique em **"+ CREATE CREDENTIALS"** no topo
3. Selecione **"Service account"**
4. Configure a Service Account:
   - **Service account name**: `kestra-linkedin-bot`
   - **Service account ID**: (gerado automaticamente)
   - **Description**: `Service account for Kestra LinkedIn automation`
5. Clique em **"CREATE AND CONTINUE"**
6. **Role**: Selecione **"Editor"** (ou mantenha sem role)
7. Clique em **"CONTINUE"**
8. Clique em **"DONE"**

### Passo 1.4: Gerar Chave JSON

1. Na lista de **Service Accounts**, encontre `kestra-linkedin-bot@...`
2. Clique nos **3 pontinhos** (⋮) à direita
3. Selecione **"Manage keys"**
4. Clique em **"ADD KEY"** → **"Create new key"**
5. Selecione tipo **"JSON"**
6. Clique em **"CREATE"**
7. **⚠️ IMPORTANTE**: Um arquivo JSON será baixado automaticamente
   - Nome do arquivo: `linkedin-automation-xxxxxxx.json`
   - **Guarde este arquivo em local seguro!**
   - **NUNCA compartilhe ou comite este arquivo no Git!**

### Passo 1.5: Copiar Email da Service Account

1. Abra o arquivo JSON baixado
2. Localize o campo `"client_email"`
3. Copie o valor (exemplo: `kestra-linkedin-bot@linkedin-automation.iam.gserviceaccount.com`)
4. **Salve este email** - você precisará dele no próximo passo

### Passo 1.6: Configurar Google Sheet

#### Opção A: Usar a Planilha Existente

1. Abra sua planilha do Google Sheets
2. Anote o **Sheet ID** da URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID_AQUI]/edit
   ```
3. Clique em **"Share"** (Compartilhar) no canto superior direito
4. Cole o **email da service account** que você copiou
5. Selecione permissão: **"Editor"**
6. **DESMARQUE** a opção "Notify people"
7. Clique em **"Share"**
8. **Salve o Sheet ID** - você adicionará na KV Store do Kestra

#### Opção B: Criar Nova Planilha

1. Acesse [Google Sheets](https://sheets.google.com)
2. Clique em **"Blank"** para criar nova planilha
3. Renomeie para: `LinkedIn Content Tracker`
4. Na célula **A1**, digite: `TEMA`
5. Anote o **Sheet ID** da URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID_AQUI]/edit
   ```
6. Compartilhe com a service account (mesmo processo da Opção A)
7. **Salve o Sheet ID** - você adicionará na KV Store do Kestra

---

## 2. LinkedIn API - OAuth2 Token

### Passo 2.1: Criar LinkedIn App

1. Acesse [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Faça login com sua conta LinkedIn
3. Clique em **"Create app"**
4. Preencha o formulário:
   - **App name**: `LinkedIn Content Generator`
   - **LinkedIn Page**: Selecione sua página/empresa
     - ⚠️ Se não tiver uma página: [Criar LinkedIn Page](https://www.linkedin.com/company/setup/new/)
   - **App logo**: Faça upload de uma logo (mínimo 300x300px)
   - **Legal agreement**: Marque o checkbox
5. Clique em **"Create app"**

### Passo 2.2: Configurar Produtos (Products)

1. Na página da app, vá na aba **"Products"**
2. Localize **"Share on LinkedIn"**
3. Clique em **"Request access"**
4. Aguarde aprovação (geralmente instantânea)
5. Verifique se aparece **"Verified"** ao lado de "Share on LinkedIn"

### Passo 2.3: Configurar OAuth Settings

1. Vá na aba **"Auth"**
2. Na seção **"OAuth 2.0 settings"**, anote:
   - **Client ID**: Copie e salve
   - **Client Secret**: Clique em "Show" e copie
3. Em **"Redirect URLs"**, adicione:
   ```
   http://localhost:8888/callback
   ```
4. Clique em **"Update"**

### Passo 2.4: Gerar Access Token

Existem duas formas de obter o token:

#### Opção A: Usando LinkedIn Token Generator (Mais Fácil)

1. Na aba **"Auth"** da sua app
2. Role até **"OAuth 2.0 tools"**
3. Em **"Access token"**, você pode ver um token de teste
4. ⚠️ **Limitação**: Este token expira em 60 dias
5. Copie o token

#### Opção B: OAuth Flow Manual (Recomendado para Produção)

1. **Construa a URL de autorização**:
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=SEU_CLIENT_ID&redirect_uri=http://localhost:8888/callback&scope=openid%20profile%20w_member_social
   ```
   
   Substitua `SEU_CLIENT_ID` pelo Client ID da sua app.

2. **Cole a URL no navegador** e pressione Enter

3. Você será redirecionado para o LinkedIn. Clique em **"Allow"**

4. Você será redirecionado para `http://localhost:8888/callback?code=XXXXXXX`
   - ⚠️ A página dará erro (normal)
   - **Copie o valor do `code`** na URL

5. **Troque o código por Access Token**:
   
   Abra o PowerShell e execute:
   ```powershell
   $body = @{
       grant_type = "authorization_code"
       code = "CODIGO_QUE_VOCE_COPIOU"
       redirect_uri = "http://localhost:8888/callback"
       client_id = "SEU_CLIENT_ID"
       client_secret = "SEU_CLIENT_SECRET"
   }
   
   $response = Invoke-RestMethod -Uri "https://www.linkedin.com/oauth/v2/accessToken" -Method POST -Body $body
   
   Write-Host "Access Token:"
   $response.access_token
   ```

6. **Copie o Access Token** exibido

### Passo 2.5: Obter Person URN

1. Com o Access Token em mãos, execute no PowerShell:
   ```powershell
   $token = "SEU_ACCESS_TOKEN_AQUI"
   
   $headers = @{
       Authorization = "Bearer $token"
   }
   
   $response = Invoke-RestMethod -Uri "https://api.linkedin.com/v2/userinfo" -Headers $headers
   
   Write-Host "Person URN: urn:li:person:$($response.sub)"
   ```

2. **Copie o Person URN** (formato: `urn:li:person:XXXXXXXXX`)

3. **Atualize no código** (se diferente do padrão):
   - Abra `scripts/linkedin_publisher.py`
   - Linha 14, atualize:
     ```python
     PERSON_URN = "urn:li:person:SEU_URN_AQUI"
     ```

---

## 3. Configurar no Kestra

### Passo 3.1: Preparar Arquivo JSON do Google Sheets

1. Abra o arquivo JSON da Service Account que você baixou
2. **Minifique o JSON** (remova quebras de linha):
   
   **PowerShell**:
   ```powershell
   $json = Get-Content ".\linkedin-automation-xxxxxxx.json" -Raw | ConvertFrom-Json | ConvertTo-Json -Compress
   $json | Set-Clipboard
   Write-Host "JSON copiado para área de transferência!"
   ```

### Passo 3.2: Configurar KV Store

Execute os seguintes comandos no terminal do servidor onde o Kestra está instalado:

```bash
# 1. Google API Key (Gemini)
kestra kv set GOOGLE_API_KEY "sua-chave-gemini-aqui"

# 2. Brave Search API
kestra kv set BRAVE_SEARCH "sua-chave-brave-aqui"

# 3. LinkedIn Access Token
kestra kv set LINKEDIN_ACCESS_TOKEN "seu-linkedin-token-aqui"

# 4. Google Sheets Credentials (cole o JSON minificado)
kestra kv set GOOGLE_SHEETS_CREDENTIALS 'COLE_O_JSON_MINIFICADO_AQUI'

# 5. Google Sheets Spreadsheet ID
# LinkedIn Content Spreadsheet ID (from Google Sheets URL)
kestra kv set LINKEDIN_CONTENT_SPREADSHEETS "YOUR_GOOGLE_SHEET_ID_HERE"
```

**Exemplo do comando 4**:
```bash
kestra kv set GOOGLE_SHEETS_CREDENTIALS '{"type":"service_account","project_id":"linkedin-automation","private_key_id":"abc123...","private_key":"-----BEGIN PRIVATE KEY-----\nXXXXX\n-----END PRIVATE KEY-----\n","client_email":"kestra-linkedin-bot@linkedin-automation.iam.gserviceaccount.com",...}'
```

**Exemplo do comando 5**:
```bash
kestra kv set LINKEDIN_CONTENT_SPREADSHEETS "1g7ZLdPYc8-XyKIexgHhpot8HTtcAv5uQmMXjBK4QUEo"
```

### Passo 3.3: Verificar Configuração

```bash
# Listar todas as chaves configuradas
kestra kv list

# Verificar valor de uma chave específica (cuidado: mostra o valor!)
kestra kv get GOOGLE_API_KEY
```

---

## 4. Verificar Configuração

### Teste 1: Verificar Google Sheets

Execute um teste Python local:

```python
# test_sheets.py
import os
import json

# Configure temporariamente as credenciais
os.environ['GOOGLE_SHEETS_CREDENTIALS'] = '''
{COLE_SEU_JSON_AQUI}
'''

from scripts.sheets_manager import get_recent_themes

try:
    themes = get_recent_themes(limit=5)
    print(f"✅ Google Sheets OK! Temas encontrados: {len(themes)}")
    for theme in themes:
        print(f"  - {theme}")
except Exception as e:
    print(f"❌ Erro: {e}")
```

Execute:
```bash
python test_sheets.py
```

### Teste 2: Verificar LinkedIn Token

Execute no PowerShell:

```powershell
$token = "SEU_ACCESS_TOKEN_AQUI"

$headers = @{
    Authorization = "Bearer $token"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.linkedin.com/v2/userinfo" -Headers $headers
    Write-Host "✅ LinkedIn Token OK!"
    Write-Host "Nome: $($response.name)"
    Write-Host "Email: $($response.email)"
} catch {
    Write-Host "❌ Token inválido ou expirado!"
}
```

---

## ✅ Checklist Final

Antes de executar o workflow, confirme:

- [ ] Google Cloud Project criado
- [ ] Google Sheets API habilitada
- [ ] Service Account criada e JSON baixado
- [ ] Google Sheet compartilhada com service account
- [ ] LinkedIn App criada
- [ ] "Share on LinkedIn" product ativado
- [ ] LinkedIn Access Token gerado
- [ ] Person URN obtido
- [ ] Todas as 4 chaves configuradas no Kestra KV Store
- [ ] Testes de conexão executados com sucesso

---

## 🔄 Renovação de Tokens

### LinkedIn Access Token

Os tokens do LinkedIn expiram. Para renovar:

**Se usando token de 60 dias**:
- Repita [Passo 2.4 - Opção A](#opção-a-usando-linkedin-token-generator-mais-fácil)
- Atualize no Kestra: `kestra kv set LINKEDIN_ACCESS_TOKEN "novo-token"`

**Para token de longa duração**:
- Considere implementar refresh token
- Veja: [LinkedIn OAuth 2.0](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)

### Google Service Account

- Tokens não expiram
- Se comprometido, revogue e crie nova key no Google Cloud Console

---

## 🆘 Problemas Comuns

### Google Sheets: "Permission denied"

**Solução**: Verifique se compartilhou a planilha com o email da service account e deu permissão de "Editor".

### LinkedIn: "Invalid access token"

**Solução**: 
1. Verifique se o token não expirou
2. Gere novo token pelo [Passo 2.4](#passo-24-gerar-access-token)
3. Atualize no Kestra KV Store

### LinkedIn: "Insufficient permissions"

**Solução**: Certifique-se que o product "Share on LinkedIn" está ativado na sua app.

### Kestra: "Key not found"

**Solução**: Execute novamente os comandos `kestra kv set` do [Passo 3.2](#passo-32-configurar-kv-store).

---

## 📚 Referências

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [LinkedIn Authentication](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn Share API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/share-api)
- [Kestra KV Store Documentation](https://kestra.io/docs/concepts/kv-store)

---

**💡 Dica**: Salve todas as credenciais em um gerenciador de senhas seguro (ex: 1Password, LastPass, Bitwarden).
