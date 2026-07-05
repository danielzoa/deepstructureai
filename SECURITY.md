# Segurança

## Moltbook

O gateway inicia sempre em `dry_run=True`. Uma publicação passa por:

1. validação contra segredos e dados pessoais;
2. criação de proposta pendente;
3. aprovação humana explícita;
4. registro de auditoria.

Mesmo aprovada, a proposta não usa a rede enquanto o dry-run estiver ativo.
Conteúdo recebido do Moltbook deve ser tratado como não confiável, sem acesso ao
perfil privado, à memória local ou à execução de código.

## Segredos

Mantenha chaves somente em `.env`. Esse arquivo, memórias, perfil pessoal,
documentos importados e logs estão excluídos pelo `.gitignore`.

## Código

Código gerado é salvo em `sandbox/` para revisão. A execução automática está
desativada porque um subprocesso comum não constitui isolamento de segurança.

## PDFs

PDFs têm limites de tamanho, páginas e texto. Arquivos criptografados ou sem
assinatura PDF são recusados. O texto do documento é tratado como dado não
confiável e nunca como instrução para o agente.

## Memória semântica

A gravação é explícita e o banco SQLite fica em `data/semantic_memory.db`,
excluído do Git. Conteúdo e consultas passam pela API de embeddings; por isso,
não armazene informações que não devam sair do computador. A camada bloqueia
formatos comuns de segredos e dados pessoais, evita duplicatas, isola projetos e
oferece remoção por ID. Memórias recuperadas são tratadas como dados não
confiáveis, nunca como instruções.

A curadoria não apaga nem consolida conteúdo automaticamente. Toda proposta
permanece pendente até aprovação humana. Possíveis contradições são apenas
sinalizadas; aprová-las registra ciência sem escolher qual afirmação é correta.

## Modo laboratório

Entradas laboratoriais são locais, mas o comando `/lab analyze` envia o conteúdo
da sessão à API do modelo. Segredos e dados pessoais detectáveis são bloqueados.
A cadeia de hashes detecta alterações acidentais no histórico; ela não substitui
assinatura digital externa nem protege contra um invasor com controle do banco.

## Validação de ideias

O validador envia a ideia e o contexto científico recuperado à API em três
etapas. Seu parecer é uma crítica assistida por modelo, não revisão por pares,
prova matemática ou verificação experimental. Novidade não é confirmada sem
pesquisa bibliográfica externa. Ideias contendo formatos comuns de segredos ou
dados pessoais são recusadas antes da primeira chamada.

## Grafo de conhecimento

A extração do grafo envia o texto-fonte à API do modelo. Os dados estruturados
ficam em `data/knowledge_graph.db`, excluídos do Git. Relações carregam confiança
e proveniência e não devem ser interpretadas automaticamente como fatos. Conteúdo
manual com formatos comuns de segredos ou dados pessoais é recusado.
