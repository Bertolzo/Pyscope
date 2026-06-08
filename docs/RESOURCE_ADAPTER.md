# Resource Adapter Review

Este documento descreve o módulo `tools/resource_adapter.py`, que foi criado para
suportar execuções controladas de tarefas pesadas como a observação C1 de
projetos grandes (por exemplo Django).

## Objetivo

O adaptador oferece:

- detecção de recursos disponíveis no host (memória total e núcleos de CPU);
- detecção de limites de cgroup/container quando disponíveis;
- recomendações de `nice`, `cpulimit` e limite de memória para minimizar o
  impacto em serviços críticos;
- wrapper para executar um comando sob `nice` e `cpulimit` com timeout opcional.

## Quando usar

Use este módulo quando for necessário:

- rodar análise de repositórios grandes em máquinas com RAM limitada;
- executar jobs stresseantes sem prejudicar serviços críticos no mesmo host;
- validar se o processo deve ser restrito a uma porcentagem menor de CPU e
  memória;
- documentar e aplicar uma política de execução mais segura para comandos de
  pipeline.

## Como funciona

### Detecção de ambiente

O adaptador faz as seguintes verificações:

- lê `/proc/meminfo` para identificar memória total do sistema;
- lê `/proc/1/cgroup` para detectar se está dentro de container Docker/Kubernetes;
- lê arquivos de cgroup:
  - `/sys/fs/cgroup/memory.max` ou
    `/sys/fs/cgroup/memory/memory.limit_in_bytes` para limites de memória;
  - `/sys/fs/cgroup/cpu.max` ou
    `/sys/fs/cgroup/cpu/cpu.cfs_quota_us` e
    `/sys/fs/cgroup/cpu/cpu.cfs_period_us` para limites de CPU.

### Recomendação de limites

A função `recommend_limits()` calcula:

- `recommended_nice`: valor de prioridade do processo;
- `recommended_cpu_percent`: limite percentual de CPU para `cpulimit`;
- `recommended_memory_limit_bytes`: memória sugerida para o job.

O modo `prefer_low_impact=True` aplica recomendações mais conservadoras:

- `nice=10`
- `cpulimit<=50%`
- memória entre 40% e 50% do total disponível, com reserva de 1 GiB para o
  sistema.

Quando `prefer_low_impact=False`, o módulo é mais agressivo e permite até 90%
ou o equivalente aos núcleos disponíveis.

### Execução com limites

A função `run_command_with_limits(cmd, cpu_percent, nice, timeout)` cria um
wrapper que executa:

- `cpulimit -l <cpu_percent> -- <cmd>` quando `cpulimit` está instalado;
- `nice -n <nice> sh -c '<cmd>'` para reduzir prioridade do processo;
- se `timeout` for fornecido, aplica `subprocess.run(..., timeout=timeout)`.

## Free-tier fallback

O adaptador também suporta recomendações de execução remota usando um
fallback de free-tier / promoções de cloud. Isso é útil quando seu PC local
não tem recursos suficientes para concluir um job pesado como Django.

Você pode listar opções de free-tier conhecidas com:

```bash
./.venv/bin/python tools/resource_adapter.py --list-freetier
```

E atualizar o cache de promoções com:

```bash
./.venv/bin/python tools/resource_adapter.py --refresh-freetier-cache
```

O cache é armazenado em `tools/freetier_promotions_cache.json` e o módulo usa
uma lista de fallback quando a busca online falhar.

Quando o host local tiver recursos abaixo do recomendado, o comando
`--recommend` também mostrará sugestões de fallback remoto. Isso permite
que você avalie executar o job em um ambiente free-tier em vez de sobrecarregar
seu PC.

Para um protocolo enxuto de fallback automatizado e humano, veja também
`docs/FALLBACK_PROTOCOL.md`.

O critério atual sugere fallback remoto para hosts com menos de 8 GiB de RAM,
ou menos de 4 CPUs, ou quando `prefer_low_impact=True` em máquinas com menos de
12 GiB de RAM.

A opção `--fallback-if-insufficient` faz com que `--run` não execute localmente
quando a máquina for considerada fraca, e mostre apenas as opções free-tier.

## Exemplos de uso

Recomendação de limites no host atual:

```bash
./.venv/bin/python tools/resource_adapter.py --recommend
```

Execução controlada de um job Django sob limites conservadores:

```bash
./.venv/bin/python tools/resource_adapter.py --run "./.venv/bin/python tools/c1_observe.py Django https://github.com/django/django.git c1_django_limited" --prefer-low-impact --cpu 50 --nice 10 --timeout 3600
```

Forçar fallback remoto quando o host for insuficiente (não roda localmente):

```bash
./.venv/bin/python tools/resource_adapter.py --run "./.venv/bin/python tools/c1_observe.py Django https://github.com/django/django.git c1_django_limited" --fallback-if-insufficient
```

Uso automatizado com wrapper seguro:

```bash
./.venv/bin/python tools/run_c1_safely.py Django https://github.com/django/django.git c1_django_limited --prefer-low-impact --timeout 3600
```

O wrapper primeiro verifica se o host recomenda fallback remoto. Se a máquina for considerada fraca, ele interrompe a execução local e imprime as opções de free-tier.

## Uso para humano

- Rode `python tools/resource_adapter.py --recommend` para ver se a sua máquina atual é adequada.
- Se o resultado indicar fallback remoto, abra um serviço free-tier ou VM remota recomendada.
- Use `--run` local com `--prefer-low-impact` se quiser tentar no seu PC com segurança.
- Use `--fallback-if-insufficient` se quiser evitar qualquer execução local em máquinas fracas.

## Uso para máquina / script

- Em scripts de automação, use a saída de `--recommend` para decidir entre local e remoto.
- Para execução condicional, chame:

```bash
if ./.venv/bin/python tools/resource_adapter.py --recommend --prefer-low-impact | grep -q "Remote free-tier fallback recommended"; then
  echo "Use remote free-tier fallback instead"
else
  ./.venv/bin/python tools/resource_adapter.py --run "./.venv/bin/python tools/c1_observe.py Django https://github.com/django/django.git c1_django_limited" --prefer-low-impact --cpu 50 --nice 10 --timeout 3600
fi
```

- Para forçar a decisão automática de não executar localmente em um host insuficiente:

```bash
./.venv/bin/python tools/resource_adapter.py --run "./.venv/bin/python tools/c1_observe.py Django https://github.com/django/django.git c1_django_limited" --fallback-if-insufficient
```

## Resultados esperados

O módulo produz saídas semelhantes a:

- `Host memory: 7.7GiB`
- `CGroup memory limit: unknown`
- `CPU count: 4`
- `In container: False`
- `Recommended settings:`
  - `nice = 10`
  - `cpulimit = 50%`
  - `memory limit = 3.6GiB`

## Limitações

- `cpulimit` limita CPU, mas não aplica memória em nível de processo;
- o `memory_limit_bytes` recomendado é uma orientação e deve ser aplicada por
  outras ferramentas de container/cgroup se você precisar de enforce físico;
- a detecção de container é heurística e pode não cobrir todos os ambientes;
- o wrapper usa `sh -c`, então comandos complexos devem ser tratados com cuidado
  de escaping.

## Revisão do módulo

O módulo é adequado como ponto de entrada leve para execuções controladas.
Ele agrega duas preocupações importantes:

1. inspeção de recursos do host/container,
2. execução de comando com prioridades e limites de CPU.

Para revisão futura, vale considerar:

- adicionar suporte à limitação de memória real via `cgexec` ou `systemd-run`;
- documentar claramente que `cpulimit` não garante isolamento de memória;
- separar a lógica de detecção de ambiente da lógica de execução para testes
  unitários mais simples; e
- expandir a heurística de container para cgroup v2 em `/proc/self/cgroup`
  quando apropriado.
