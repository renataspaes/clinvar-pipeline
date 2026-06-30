# Pipeline de Dados Genômicos — ClinVar
**Trabalho de Conclusão de Curso**  
Engenharia e Administração de Sistemas de Banco de Dados  
Faculdade de Tecnologia — Unicamp | 2026  
**Autora:** Renata dos Santos Silva Paes

---

## Sobre o Projeto

Este projeto propõe e implementa uma arquitetura de dados voltada à 
extração, armazenamento e processamento analítico de dados genômicos 
públicos, utilizando o repositório ClinVar (NCBI) como estudo de caso.

O ClinVar é um repositório público que centraliza informações sobre 
variações genômicas humanas e suas relações com condições clínicas como 
doenças hereditárias e respostas a medicamentos. Seus dados são 
disponibilizados mensalmente em formato XML, com mais de 4,5 milhões 
de registros — o que torna a manipulação manual inviável para análises 
clínicas em larga escala.

A solução proposta automatiza a ingestão, transformação e modelagem 
desses dados, tornando-os acessíveis para análise e suporte à decisão 
clínica.

---

## Arquitetura da Solução

A estrutura segue a **Arquitetura Medalhão**, organizada em três camadas 
progressivas de qualidade e refinamento dos dados.

---

## Stack de Tecnologias

| Ferramenta | Função |
|---|---|
| Apache Airflow (Astronomer) | Orquestração e agendamento do pipeline |
| Docker | Conteinerização do ambiente local |
| Python | Scripts de extração via FTP do NCBI |
| Amazon S3 | Armazenamento dos arquivos XML brutos |
| Databricks | Processamento e armazenamento em camadas |
| PySpark | Transformação e modelagem dos dados |
| Delta Lake | Formato de armazenamento com versionamento e ACID |

---

## Camadas de Dados

### 🟤 Bronze
Ingestão do arquivo XML compactado do ClinVar diretamente do S3, 
sem tratamentos estruturais. Garante a persistência histórica do dado 
bruto e serve como fonte única de verdade para as camadas seguintes.

- **Tabela:** `bronze_clinvar.bronze_clinvar_raw`
- **Volume:** 4.526.918 registros
- **Operação:** OVERWRITE mensal

### 🥈 Silver
Desestruturação das tags XML aninhadas, normalização de tipos, 
filtragem por qualidade clínica e padronização semântica.

| Tabela | Descrição | Registros |
|---|---|---|
| silver_clinvar_variants | Núcleo das variantes (nível VCV) | 4.526.918 |
| silver_clinvar_locations | Coordenadas genômicas (GRCh38) | 4.456.876 |
| silver_clinvar_genes | Relação N:N variantes-genes | 7.167.147 |
| silver_clinvar_traits | Condições clínicas via MedGen | 6.884.746 |
| silver_clinvar_assertions | Laudos individuais por laboratório | 5.907.384 |
| silver_clinvar_clinical_summary | Consenso global por variante | 3.968.941 |

**Filtros aplicados:**
- Localizações: apenas assembly de referência **GRCh38**
- Assertions e clinical_summary: status de revisão com critérios 
fornecidos (mínimo 1 estrela no sistema ClinVar)
- Traits: campos nulos padronizados como `NOT PROVIDED`

### 🥇 Gold
Modelagem dimensional Star Schema adaptada para suporte a consultas analíticas 
e ferramentas de BI. Chaves substitutas geradas via SHA-256.

| Tabela | Tipo | Descrição |
|---|---|---|
| dim_variants_gold | Dimensão | Perfil mestre da variante com localização GRCh38 |
| dim_genes_gold | Dimensão | Catálogo único de genes (consultado independentemente) |
| dim_traits_gold | Dimensão | Catálogo único de condições clínicas via MedGen |
| fato_submissoes | Tabela Fato | Laudos individuais (nível SCV) ligados a dim_variants |

> **Nota de modelagem:** `dim_genes` e `dim_traits` possuem relação 
> N:N com variantes e são consultadas independentemente da tabela fato. 
> A implementação de bridge tables é proposta como evolução futura.

---

## Orquestração — DAG clinvar_ingestion_v1
- **Agendamento:** primeiros 7 dias do mês, às sextas-feiras
- **Alinhamento:** ciclo oficial de publicação do NCBI
- **Rastreabilidade:** arquivos renomeados com data de referência
- **Integração Airflow → Databricks:** via token de acesso com 
  permissões restritas à execução de Jobs

---

## Como Executar

### Pré-requisitos
- Docker Desktop instalado
- Astro CLI instalado (`pip install astro`)
- Conta AWS com bucket S3 configurado
- Conta Databricks (versão gratuita é suficiente para estudo)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/clinvar-data-pipeline
cd clinvar-data-pipeline

# 2. Configure as variáveis de ambiente
# Crie um arquivo .env com suas credenciais AWS e Databricks
# (veja o arquivo .env.example)

# 3. Inicialize o Airflow via Astro CLI
astro dev start

# 4. Acesse o Airflow em http://localhost:8080
# Usuário: admin | Senha: admin

# 5. Ative a DAG clinvar_ingestion_v1 e aguarde a execução
```

### Ordem de execução dos notebooks (manual)


---

## Limitações Conhecidas

- Dependência do ciclo de publicação mensal do NCBI via FTP
- Processamento executado em versões gratuitas das ferramentas,
  com restrições de recursos computacionais
- `dim_genes` e `dim_traits` não possuem ligação direta com a 
  tabela fato devido à relação N:N (sem bridge tables)
- Fonte única de dados (ClinVar) — sem integração com gnomAD, 
  OMIM ou ClinGen

---

## Trabalhos Futuros

- Substituição do FTP pela API do NCBI para atualizações mais frequentes
- Implementação de bridge tables para modelagem N:N completa
- Integração com gnomAD, OMIM e ClinGen para enriquecimento das variantes
- Dashboards analíticos em Power BI ou Tableau sobre a camada Gold
- Migração para versões pagas das ferramentas para uso em produção


---

## Referências Principais

- REIS, Joe; HOUSLEY, Matt. *Fundamentos de Engenharia de Dados*. 
  Novatec Editora, 2023.
- NCBI. *ClinVar: About ClinVar*. Disponível em: 
  https://www.ncbi.nlm.nih.gov/clinvar/intro/
- DATABRICKS. *O que é o Delta Lake?* Disponível em: 
  https://docs.databricks.com/aws/pt/delta/