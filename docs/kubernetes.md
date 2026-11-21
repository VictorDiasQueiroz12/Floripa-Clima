# Kubernetes local — Floripa-Clima

> Laboratório de desenvolvimento com Ubuntu/WSL2, Docker Desktop e Minikube. Este guia documenta a implantação observada em 21/11/2026; **não** é uma configuração pronta para produção.

## Componentes

| Componente | Kubernetes | Observação |
|---|---|---|
| Nginx/frontend | Deployment + ClusterIP Service | Proxy para `backend:8000` |
| FastAPI/backend | Deployment + ClusterIP Service | `/saude`, `/clima`, `/importar` |
| PostgreSQL 16 | StatefulSet + Headless Service + PVC | Armazenamento independente do Docker Compose |
| Alembic | Job | Migrações antes de disponibilizar o backend |
| Configurações | ConfigMap | Host/portas, sem credenciais |
| Credenciais | Secret | Gerado localmente a partir do `.env`; não versionado |
| Escala | Metrics Server + HPA | CPU alvo 60%, de 2 a 5 réplicas |

### Fluxo

```text
Navegador --localhost:8082--> port-forward --> frontend Service
                                                |
                                             Nginx
                                                | /clima /importar /saude
                                                v
                                         backend Service
                                                |
                                          FastAPI Pods
                                                |
                                            db:5432
                                                |
                                         PostgreSQL Pod
                                                |
                                            PVC 2Gi

Alembic Job -> PostgreSQL (antes do backend)
Metrics Server -> HPA -> Deployment backend
```

## Pré-requisitos

- Docker funcionando sem `sudo` com integração WSL2, se aplicável.
- Minikube com driver Docker; `kubectl` configurado.
- Recursos suficientes para o nó, imagens e até cinco réplicas do backend.
- Internet para baixar as imagens base, dependências e dados de Open-Meteo.
- Arquivo `.env` local com `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`. **Não publique valores no Git.**

Na raiz do repositório:

```bash
docker ps
minikube start --driver=docker --cpus=2 --memory=4096
kubectl get nodes
```

O driver e a capacidade devem ser adequados à máquina. A saída de `kubectl top nodes` pode mostrar a capacidade lógica do ambiente, não necessariamente o limite de RAM solicitado ao Minikube.

## Instalação do zero

**Não execute a seção de instalação como limpeza/reinstalação sobre um ambiente que contenha dados importantes.** O banco do Kubernetes é independente do volume do Docker Compose.

### 1. Namespace e ConfigMap

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
```

### 2. Secret local (não existe manifesto com senhas no repositório)

```bash
kubectl create secret generic floripa-clima-secret \
  --from-env-file=.env -n floripa-clima
kubectl describe secret floripa-clima-secret -n floripa-clima
```

O `describe` mostra as chaves e tamanhos, não os valores. Secrets **não são automaticamente criptografados em repouso**, e quem possui privilégios de leitura na API do Kubernetes pode acessá-los. Limite o acesso ao cluster e não salve exports de Secrets em repositórios. Alterar o Secret não altera automaticamente as credenciais de um banco que já foi inicializado; isso exige procedimento explícito de rotação de senha.

### 3. Armazenamento e banco

```bash
kubectl get storageclass
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl rollout status statefulset/postgres -n floripa-clima
kubectl get pvc,pods -n floripa-clima
```

O manifesto usa `standard` (StorageClass padrão observada no Minikube). Outros clusters podem exigir outra StorageClass. O PVC usa `ReadWriteOnce` e foi projetado para **um único PostgreSQL**, não para escalar o banco. O provisionador local do Minikube tem política de recuperação `Delete`: excluir o PVC pode apagar os dados. Faça backups antes de qualquer ação destrutiva.

### 4. Construir e carregar imagens locais

```bash
docker build -f backend/Dockerfile -t floripa-clima-backend:k8s .
docker build -f frontend/Dockerfile -t floripa-clima-frontend:k8s .
minikube image load floripa-clima-backend:k8s
minikube image load floripa-clima-frontend:k8s
minikube image ls | grep floripa-clima
```

Os manifests usam `imagePullPolicy: Never`, **somente para Minikube**. Para CI ou clusters remotos, publique imagens versionadas em um registry e substitua `image` e `imagePullPolicy`. Evite reutilizar sempre a mesma tag em atualizações; gere versões únicas e faça `rollout`.

### 5. Rodar migrations antes do backend

```bash
kubectl apply -f k8s/migrations-job.yaml
kubectl wait --for=condition=complete job/floripa-clima-migrations -n floripa-clima --timeout=180s
kubectl logs -n floripa-clima job/floripa-clima-migrations
```

A primeira migration cria `public.weather_daily` (revisão `4e5f2211361d`). Caso o Job falhe, inspecione `kubectl describe job` e seus logs **antes** de iniciar a API. `kubectl apply` de um Job já concluído **não executa uma nova migration**. Para uma nova revisão, crie um Job novo com nome versionado ou siga um procedimento de atualização que preserve o histórico e o banco; nunca apague o PVC para tentar corrigir migrations.

### 6. Backend, frontend e HPA

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl rollout status deployment/backend -n floripa-clima
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl rollout status deployment/frontend -n floripa-clima

minikube addons enable metrics-server
kubectl top pods -n floripa-clima
kubectl apply -f k8s/backend-hpa.yaml
kubectl get hpa -n floripa-clima
```

A meta de CPU do HPA é calculada sobre `requests.cpu=100m`, **não** sobre o limite de `500m`. O HPA controla `replicas`: por isso o arquivo `backend-deployment.yaml` não declara esse campo. Não faça `kubectl scale` manual enquanto estiver validando o HPA.

### 7. Acessar no host

Em dois terminais diferentes, mantenha estes processos ativos:

```bash
kubectl port-forward -n floripa-clima service/frontend 8082:80
```

```bash
kubectl port-forward -n floripa-clima service/backend 8001:8000
```

| Endereço | Uso |
|---|---|
| http://localhost:8082 | Dashboard Nginx |
| http://localhost:8082/saude | Health da API via Nginx |
| http://localhost:8082/clima | JSON via Nginx e API |
| http://localhost:8001/docs | Swagger FastAPI |

O port-forward precisa continuar executando, e as portas locais precisam estar livres. `curl: (52) Empty reply from server` pode ser causado por um port-forward que perdeu o Pod durante um rollout; encerre-o e abra novamente. Confira `ss -ltnp` para conflitos de porta.

## Verificações e evidências

```bash
kubectl get pods,deploy,svc,hpa -n floripa-clima
kubectl get pvc -n floripa-clima
kubectl logs -n floripa-clima deployment/backend --tail=30
kubectl logs -n floripa-clima deployment/frontend --tail=30
kubectl describe hpa backend-hpa -n floripa-clima
curl -i http://localhost:8082/saude
curl -i http://localhost:8082/clima
```

`GET /saude` informa que a API está ativa, mas **não verifica o banco**. A rota `/clima` executa uma consulta real ao PostgreSQL, portanto é melhor para validar a comunicação com o banco. Uma base nova retorna inicialmente `{"total":0,"registros":[]}`.

### Resultados observados em 21/11/2026

- PostgreSQL 16: Pod `postgres-0` `1/1 Running`, PVC `2Gi Bound`.
- Alembic: Job `Complete 1/1`; revisão `4e5f2211361d` aplicada.
- Frontend e backend: Pods `Running`; Nginx retornou 200 em `/`, `/clima`, `/importar` e `/saude`.
- Importação testada entre 01/01/2025 e 10/01/2025; `GET /clima` retornou dez registros.
- Recuperação automática: exclusão de um Pod do backend resultou na criação de outro.
- HPA: meta de CPU 60%; sob carga sintética, aumentou de 2 para 4 e para 5 réplicas, com `5/5 Ready`.
- Após a carga: `SuccessfulRescale: New size: 2; reason: All metrics below target`, com `2/2 Ready`.

Esses resultados são **observações de um laboratório local**. Não constituem benchmark de throughput, validação de alta disponibilidade do banco ou teste de produção.

### Segurança e limitações antes de produção

- Banco com uma única réplica e hostpath local: **não é tolerante à perda do nó**. Planeje backups e restauração testada.
- `/importar` está exposto na interface e realiza consultas externas e gravações: adicione autenticação/autorização, limites de requisição e controle de concorrência antes de exposição pública.
- Rotas `/saude` e probes atuais verificam HTTP da API, não saúde do PostgreSQL.
- Secrets devem ter RBAC restrito e, em produção, criptografia em repouso/gerenciamento externo de segredos.
- Defina imagens versionadas, scanning de vulnerabilidades, políticas de rede, TLS e execução com privilégios mínimos em implantação de produção.
- Os requests/limits atuais são valores iniciais de laboratório, não foram dimensionados para carga real.
- No WSL2 com projeto em `/mnt/c`, ajustes de permissão do Windows podem não corresponder às permissões POSIX de uma máquina Linux nativa.

## Operação segura

```bash
# Ver recursos atuais
kubectl get pods,deploy,svc,hpa -n floripa-clima

# Parar Minikube sem excluir o cluster nem o PVC
minikube stop

# Retomar mais tarde
minikube start
```

Não use `minikube delete` ou `kubectl delete pvc postgres-pvc` para simplesmente parar a aplicação; isso pode destruir o ambiente e seus dados. Para mudanças no banco, primeiro faça um backup e planeje restauração.

## Próximos aperfeiçoamentos

1. Pipeline CI para validar YAML, lint e build de imagens.
2. Imagens com tags imutáveis em registry.
3. Verificações de conectividade do banco e métricas de aplicação.
4. Backups, restauração e testes de atualização controlada.
5. Autenticação e rate limiting em `POST /importar`, se o serviço for publicado.

Documentação oficial: [Kubernetes](https://kubernetes.io/docs/) · [Minikube](https://minikube.sigs.k8s.io/docs/) · [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).
