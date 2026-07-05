# DeepStructureAI

Assistente local de pesquisa com memória, agentes especializados, ferramentas e
uma base recuperável de conhecimento NTG.

## Iniciar

```powershell
.\.venv\Scripts\python.exe agent.py
```

## NTG

```text
/import_ntg C:\caminho\documento.pdf
/ntg
/ntg search produto generalizado
```

Importar um PDF não treina os pesos do modelo. O documento é extraído, resumido
e indexado para ser recuperado como contexto nas conversas e nos workflows.

## Memória semântica

```text
/semantic remember preferência::Prefiro argumentos matemáticos rigorosos
/semantic remember hipótese::O produto NTG pode preservar uma estrutura graduada
/semantic search Como devo apresentar uma demonstração?
/semantic list
/semantic stats
/semantic forget ID
```

As memórias são gravadas apenas por comando explícito e separadas pelo projeto
ativo. Texto e consultas são enviados à API de embeddings; os vetores e conteúdos
ficam no banco local `data/semantic_memory.db`. Senhas, tokens, e-mails e outros
dados pessoais detectáveis são recusados. `forget` remove uma memória pelo ID.

### Curadoria

```text
/semantic importance ID 1
/semantic archive ID
/semantic archived
/semantic restore ID
/curate scan
/curate pending
/curate approve ID_DA_PROPOSTA
/curate reject ID_DA_PROPOSTA
```

`scan` procura memórias muito semelhantes, possíveis contradições e itens sem uso
há mais de 180 dias. A curadoria apenas propõe: `approve` aplica uma fusão ou
arquivamento; `reject` descarta a proposta. Conflitos são somente sinalizados.
Arquivar remove a memória da recuperação normal sem apagá-la.

## Modo laboratório

```text
/lab start Regularidade de Navier-Stokes via NTG
/lab question Qual estimativa precisa ser demonstrada?
/lab hypothesis O termo tensorial produz controle coercivo
/lab assumption A solução é suave no intervalo considerado
/lab protocol Derivar a estimativa e testar os termos críticos
/lab control Comparar com o caso sem o termo tensorial
/lab falsification Procurar configuração em que a estimativa falha
/lab evidence Resultado ou referência verificável
/lab observation Comportamento observado no cálculo
/lab result Resultado obtido, com condições e limitações
/lab checklist
/lab analyze
/lab verify
/lab close
```

`start` ativa regras científicas mais estritas para todos os agentes. O caderno
é persistente, separado por projeto e possui uma cadeia de hashes para detectar
alterações acidentais. `analyze` separa fatos de inferências e registra a análise
no próprio histórico. Use `/lab abandon` para encerrar uma sessão incompleta e
`/lab list` para consultar sessões anteriores.

## Validador crítico de ideias

```text
/validate idea O produto NTG pode controlar o termo crítico da vorticidade
/validate list
/validate show ID
/validate retest ID
```

A validação usa três papéis independentes: formalizador, adversário e juiz.
O relatório explicita pressupostos, critérios de refutação, contraexemplos,
evidências ausentes e um próximo teste decisivo. `retest` cria uma nova versão
ligada à avaliação anterior. Os únicos pareceres permitidos são `promising`,
`needs_revision`, `unsupported`, `internally_inconsistent` e
`not_falsifiable`; o modelo não pode declarar uma ideia provada.

## Grafo de conhecimento

```text
/graph build
/graph stats
/graph verify
/graph search produto generalizado
/graph neighbors NTG
/graph path NTG -> controle de vorticidade
/graph ingest Texto científico manual
/graph export
```

`build` extrai nós e relações dos documentos NTG importados. Cada nó e relação
mantém tipo epistêmico, confiança e proveniência. Repetir a construção não duplica
fontes idênticas. `export` produz JSON e GraphML em `output/graph`; o GraphML pode
ser aberto em ferramentas como Gephi. O grafo é consultado automaticamente pelos
agentes, mas relações hipotéticas continuam marcadas como hipóteses.

## Moltbook seguro

```text
/moltbook propose Texto público
/moltbook pending
/moltbook approve ID
/moltbook inspect Conteúdo externo
```

O gateway está em dry-run: nenhuma publicação de rede é realizada.

## Artigos em PDF

```text
/article draft Escreva um artigo científico sobre a NTG
/article preview
/article status
/article polish
/article export artigo_ntg.pdf
```

O rascunho passa por uma segunda revisão do modelo. Somente o comando `export`
autoriza a gravação, restrita a `output/pdf/articles`. Arquivos existentes não
são sobrescritos. `polish` refina artigos antigos, remove metalinguagem editorial
e melhora o registro acadêmico. As equações usam MathText, um subconjunto seguro
de LaTeX que não executa comandos de sistema ou leitura de arquivos.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
