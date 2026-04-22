# LinkedIn Jobs Bot

Bot para buscar, filtrar e salvar vagas de emprego do LinkedIn de duas formas:

- lendo HTML salvo localmente
- coletando as vagas visiveis com Playwright em um navegador real
- enviando alertas para Telegram e Discord

## O que esta versao faz

- abre o LinkedIn Jobs com Playwright usando um perfil persistente
- permite login manual no navegador, sem automatizar credenciais
- rola a listagem para capturar mais cards visiveis
- extrai titulo, empresa, localizacao e link
- filtra por palavras-chave e localizacao
- remove duplicatas
- salva saida em `JSON`, `CSV` e um snapshot do HTML
- envia resumo das vagas filtradas para Telegram e/ou Discord
- evita alertas duplicados ao lembrar vagas ja vistas

## O que esta versao nao faz

- nao tenta burlar limites, captcha ou bloqueios
- nao faz candidatura automatica
- nao garante compatibilidade eterna com mudancas de layout do LinkedIn

## Estrutura

- `main.py`: ponto de entrada
- `src/linkedin_jobs_bot/cli.py`: CLI
- `src/linkedin_jobs_bot/collector.py`: coleta com Playwright
- `src/linkedin_jobs_bot/parser.py`: extracao de vagas do HTML salvo
- `src/linkedin_jobs_bot/storage.py`: persistencia de resultados
- `src/linkedin_jobs_bot/config.py`: leitura da configuracao
- `config.example.json`: exemplo de filtros

## Requisitos

```powershell
pip install playwright
python -m playwright install chromium
```

Para notificacoes, nao e necessario instalar biblioteca extra. O envio usa a biblioteca padrao do Python.

## Modo 1: coleta com Playwright

1. Copie `config.example.json` para `config.json`.
2. Ajuste `search_url`, filtros e pasta de perfil.
3. Rode:

```powershell
python main.py --config config.json --collect
```

Na primeira execucao, o navegador vai abrir em modo visivel. Se precisar entrar na sua conta, faca login manualmente e volte ao terminal para pressionar `Enter`.

## Modo 2: HTML salvo

```powershell
python main.py --config config.json --input .\data\linkedin-search.html
```

Ou com varios arquivos:

```powershell
python main.py --config config.json --input .\data\linkedin-search-1.html .\data\linkedin-search-2.html
```

## Saida

Por padrao, o bot grava:

- `output/jobs.json`
- `output/jobs.csv`
- `output/linkedin-search-snapshot.html`

## Dashboard web

Adicionei um frontend local com foco em visualizacao dos resultados e um painel por modalidade:

- total de vagas
- vagas remotas
- vagas hibridas
- vagas presenciais
- principais empresas
- principais localizacoes
- busca textual e filtro por modalidade

Para iniciar o dashboard:

```powershell
python dashboard.py
```

Depois abra:

```text
http://127.0.0.1:8765
```

Se quiser apontar para outro arquivo:

```powershell
python dashboard.py --jobs-file output/jobs.json --port 9000
```

## Alertas no Telegram e Discord

Preencha no `config.json` os campos desejados:

- `notify`: ativa ou desativa o envio
- `notify_max_jobs`: limita quantas vagas entram na mensagem
- `telegram_bot_token`: token do bot do Telegram
- `telegram_chat_id`: chat ou canal de destino
- `discord_webhook_url`: webhook do canal do Discord
- `state_filename`: arquivo usado para lembrar vagas ja notificadas

Se `notify` estiver como `true`, o bot tenta enviar o resumo para todos os canais configurados.

Exemplo de fluxo:

```powershell
python main.py --config config.json --collect
```

O bot coleta, filtra, salva os arquivos e dispara a notificacao ao final.

Por padrao, as notificacoes incluem apenas vagas novas em relacao as execucoes anteriores. O historico de vagas vistas fica salvo em `output/seen_jobs.json`.

## Agendamento diario no Windows

Adicionei dois scripts em [scripts/run_linkedin_jobs_bot.ps1](C:/Users/Guilherme/Desktop/LuminaProject/.github/scripts/run_linkedin_jobs_bot.ps1) e [scripts/register_daily_task.ps1](C:/Users/Guilherme/Desktop/LuminaProject/.github/scripts/register_daily_task.ps1).

O primeiro executa o bot com `--collect`. O segundo registra uma tarefa agendada diaria no Windows Task Scheduler.

Exemplo para registrar todo dia as 09:00:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_daily_task.ps1 -TaskName "LinkedInJobsBotDaily" -ScheduleTime "09:00" -ConfigPath "..\config.json"
```

Se quiser registrar sem enviar notificacoes:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_daily_task.ps1 -TaskName "LinkedInJobsBotDaily" -ScheduleTime "09:00" -ConfigPath "..\config.json" -NoNotify
```

Para rodar manualmente pelo mesmo script do agendamento:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_linkedin_jobs_bot.ps1 -ConfigPath "..\config.json"
```

Se quiser forcar notificacao como se fosse a primeira execucao, apague o arquivo de estado ou rode com:

```powershell
python main.py --config config.json --collect --reset-seen
```

## Observacoes

- O bot usa um perfil persistente em `profile_dir` para manter sua sessao entre execucoes.
- O HTML e os seletores do LinkedIn mudam com frequencia. Se a captura parar de funcionar, o primeiro ponto a revisar e `collector.py`.
- Se nenhum canal de notificacao estiver configurado, o bot continua funcionando e apenas salva os arquivos localmente.
- A tarefa agendada usa sua sessao do Windows em modo interativo. Isso ajuda quando o navegador precisa abrir para manter a coleta com Playwright.
