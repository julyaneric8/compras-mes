# 🛒 Compras do Mês

Aplicação web para organização e controle de compras mensais, desenvolvida com **Python, Flask e SQLite**.

O projeto permite criar listas de compras separadas por mês, definir um orçamento, acompanhar os gastos e consultar o histórico dos meses anteriores.

A proposta é reunir **organização de compras e controle financeiro** em uma interface simples, responsiva e intuitiva.

---

## 📸 Preview

<p align="center">
  <img
    src="screenshots/compras-mes.png"
    alt="Interface do projeto Compras do Mês"
    width="900"
  >
</p>

---

## ✨ Funcionalidades

### 🛒 Lista de compras

- Cadastro de produtos
- Edição de produtos
- Exclusão de produtos
- Preço e quantidade por item
- Organização por categorias
- Marcação de produtos como comprados
- Pesquisa por nome ou categoria
- Filtros para todos, pendentes e comprados

### 💰 Controle de orçamento

- Orçamento independente para cada mês
- Cálculo automático do valor gasto
- Cálculo do valor restante
- Percentual de utilização do orçamento
- Barra de progresso
- Indicação visual quando o orçamento é ultrapassado

### 📊 Análise de gastos

- Resumo de gastos por categoria
- Percentual gasto em cada categoria
- Identificação da categoria com maior gasto
- Histórico mensal
- Média de gastos
- Comparação com o mês anterior
- Visualização da evolução dos gastos

### 📅 Organização mensal

Os produtos são associados a um **mês e ano**.

Ao navegar entre os meses, cada período mantém sua própria lista de compras e orçamento, permitindo consultar registros anteriores sem apagar os dados já cadastrados.

---

## 🖥️ Interface

A interface foi desenvolvida com foco em simplicidade, organização e legibilidade.

O projeto utiliza:

- design minimalista;
- paleta em tons de verde;
- componentes em cards;
- indicadores visuais;
- barras de progresso;
- layout responsivo.

---

## 🛠️ Tecnologias

| Tecnologia | Utilização |
| --- | --- |
| Python | Lógica da aplicação |
| Flask | Backend e rotas HTTP |
| SQLite | Persistência dos dados |
| Jinja2 | Renderização dinâmica |
| HTML5 | Estrutura da interface |
| CSS3 | Estilização e responsividade |
| JavaScript | Interações no frontend |

---

## 🧠 Decisões técnicas

### Valores monetários em centavos

Os valores financeiros são armazenados no banco de dados como **números inteiros representando centavos**.

Exemplo:

```text
R$ 27,90 → 2790
```

Essa abordagem evita problemas de precisão associados ao uso de números de ponto flutuante em cálculos financeiros.

No backend, os valores recebidos também são tratados com `Decimal` antes de serem convertidos para centavos.

### Histórico mensal

Cada produto possui informações de **mês e ano**.

Com isso, o histórico pode ser calculado diretamente a partir dos produtos cadastrados, sem a necessidade de duplicar os dados em uma tabela separada.

### Separação de responsabilidades

O projeto mantém diferentes responsabilidades entre as tecnologias:

```text
Python / Flask → regras, cálculos e rotas
SQLite        → armazenamento dos dados
Jinja2 / HTML → estrutura e apresentação
CSS           → aparência e responsividade
JavaScript    → interações da interface
```

Os principais cálculos financeiros são realizados no backend.

---

## 📁 Estrutura do projeto

```text
compras-mes/
│
├── database/
│
├── screenshots/
│   └── compras-mes.png
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

O arquivo local do banco de dados SQLite não é incluído no repositório.

---

## 🚀 Executando o projeto localmente

### Pré-requisitos

É necessário ter o **Python** instalado no computador.

### 1. Baixe ou clone o projeto

```bash
git clone https://github.com/julyaneric8/compras-mes.git
```

Entre na pasta:

```bash
cd compras-mes
```

### 2. Crie o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute a aplicação

```bash
python app.py
```

### 6. Acesse localmente

Com a aplicação em execução, abra no navegador:

```text
http://127.0.0.1:5000
```

---

## 🗃️ Banco de dados

O projeto utiliza **SQLite**, portanto não é necessário configurar um servidor de banco de dados separado.

As principais informações armazenadas para cada produto são:

```text
Produto
├── nome
├── categoria
├── preço
├── quantidade
├── mês
├── ano
└── status de comprado
```

Os orçamentos mensais também são armazenados no banco de dados.

---

## 📱 Responsividade

A interface foi desenvolvida para se adaptar a diferentes tamanhos de tela, incluindo computadores, tablets e dispositivos móveis.

---

## 🎯 Objetivo do projeto

O projeto foi desenvolvido para colocar em prática conceitos de desenvolvimento web, incluindo:

- desenvolvimento backend com Flask;
- criação de rotas HTTP;
- formulários;
- operações CRUD;
- persistência com SQLite;
- consultas e agregações SQL;
- manipulação de valores monetários;
- templates com Jinja2;
- JavaScript no frontend;
- estilização com CSS;
- design responsivo;
- organização de um projeto web.

---

## 📄 Sobre

Projeto desenvolvido para fins de estudo e portfólio.
