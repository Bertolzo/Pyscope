# Fallback Protocol — AI + Human

Este documento é um protocolo estenográfico para acionar fallback remoto sempre
que o host local estiver fraco. Foi criado para que uma AI e um humano possam
seguir o mesmo conjunto de decisões.

## Objetivo

- Detectar quando o host local é insuficiente para jobs pesados de C1.
- Evitar execução local insegura.
- Escolher e acionar fallback remoto free-tier quando necessário.
- Manter um caminho claro para execução segura e reprodutível.

## Símbolos

- `LOCAL_OK` = host local adequado
- `LOCAL_WEAK` = host local fraco / fallback recomendado
- `AI` = agente automatizado lendo o protocolo
- `HUMANO` = operador seguindo o protocolo

## Decisão

1. Rodar recomendação:

```bash
./.venv/bin/python tools/resource_adapter.py --recommend --prefer-low-impact
```

2. Se a saída contiver:

- `Remote free-tier fallback recommended:`

  Então: `LOCAL_WEAK`

- caso contrário:

  Então: `LOCAL_OK`

3. Se `LOCAL_WEAK`, não execute localmente sem um override consciente.

4. Use `--fallback-if-insufficient` como o gatilho seguro para evitar qualquer
   execução local quando o host for fraco.

## Acionamento

- `AI`: interpretar `LOCAL_WEAK` como um sinal para escolher um host remoto
  free-tier ou um fluxo de provisionamento automático.
- `HUMANO`: tratar `LOCAL_WEAK` como um alerta de segurança e seguir para um
  provedor remoto em vez de continuar localmente.
- `FORCE_LOCAL`: só usar com plena consciência de risco de OOM / timeout.

## Ação de fallback

### Se `LOCAL_WEAK`

AI / HUMANO:

- NÃO rodar localmente.
- Usar `tools/run_c1_safely.py` com `--fallback-if-insufficient`, ou
- preferir `tools/remote_runner.py` / `tools/provision_and_run_oracle.py`.

#### Comando curto (não roda localmente)

```bash
./.venv/bin/python tools/resource_adapter.py --run "<comando>" --fallback-if-insufficient
```

#### Exemplo C1 Django

```bash
./.venv/bin/python tools/resource_adapter.py --run "./.venv/bin/python tools/c1_observe.py Django https://github.com/django/django.git c1_django_limited" --fallback-if-insufficient
```

#### Exemplo de fallback remoto genérico

```bash
./.venv/bin/python tools/remote_runner.py --host <IP> --user <USER> --key /path/to/key --project Django --repo-url https://github.com/django/django.git --workdir-name c1_django_remote
```

#### Exemplo de fallback AWS CLI

```bash
./.venv/bin/python tools/provision_and_run_aws.py --execute --project Django --repo-url https://github.com/django/django.git --destroy
```

#### Exemplo de fallback OCI SDK

```bash
./.venv/bin/python tools/provision_and_run_oci_sdk.py --compartment-id <COMPARTMENT_OCID> --availability-domain <AD> --project Django --repo-url https://github.com/django/django.git --destroy
```

#### Exemplo de fallback Oracle CLI

```bash
./.venv/bin/python tools/provision_and_run_oracle.py --compartment-id <COMPARTMENT_OCID> --availability-domain <AD> --execute --project Django --repo-url https://github.com/django/django.git --destroy
```

### Se `LOCAL_OK`

AI / HUMANO:

- rodar localmente com limites conservadores.

#### Comando curto local seguro

```bash
./.venv/bin/python tools/run_c1_safely.py Django https://github.com/django/django.git c1_django_limited --prefer-low-impact --cpu 50 --nice 10 --timeout 7200
```

## Regras de acionamento

| Condição | Ação | Ferramenta |
|---|---|---|
| `LOCAL_WEAK` e `--fallback-if-insufficient` | Não executar local | `tools/resource_adapter.py` |
| `LOCAL_WEAK` e fallback remoto desejado | Criar/executar VM remota | `tools/remote_runner.py` ou `tools/provision_and_run_oracle.py` |
| `LOCAL_OK` | Executar local seguro | `tools/run_c1_safely.py` |

## Procedimento AI explicito

1. Executar `tools/resource_adapter.py --recommend --prefer-low-impact`.
2. Se output indicar fallback remoto:
   - imprimir "REMOTE FALLBACK" e parar local.
   - escolher provedor free-tier usando `--list-freetier`.
   - acionar `tools/remote_runner.py` se host remoto já existir.
   - acionar `tools/provision_and_run_oracle.py --execute` se usar Oracle e tiver credenciais.
3. Se output não indicar fallback remoto:
   - acionar `tools/run_c1_safely.py` com `--prefer-low-impact` e limites.

## Procedimento humano rápido

1. Rodar `./.venv/bin/python tools/resource_adapter.py --recommend --prefer-low-impact`.
2. Ler se há `Remote free-tier fallback recommended:`.
3. Se houver, não rode localmente; escolha remote provider e use os scripts de fallback.
4. Se não houver, rode localmente com `tools/run_c1_safely.py`.

## Fallback providers

Use `tools/resource_adapter.py --list-freetier` para ver as opções atuais.

- AWS Free Tier
- Google Cloud Free Tier
- Oracle Cloud Free Tier
- Fly.io Free Plan
- Railway Free Tier

## Exemplo estenográfico de acionamento

- `IF fallback_recommended THEN remote_run`
- `ELSE safe_local_run`
- remote_run = `remote_runner` ou `provision_and_run_oracle`
- safe_local_run = `run_c1_safely`

## Notas

- `--fallback-if-insufficient` é a bandeira de segurança para impedir qualquer execução local.
- `--skip-if-insufficient` funciona como alias do mesmo comportamento.
- Use `--force-local` somente se estiver absolutamente certo que o host pode suportar o job.
