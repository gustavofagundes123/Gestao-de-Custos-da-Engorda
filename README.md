# 🐂 Gestão de Custos da Engorda

> **Sistema web para gerenciamento de custos e cálculo do custo por quilograma produzido na engorda de bovinos.**

---

## 📌 Sobre o Projeto

O **Gestão de Custos da Engorda** é uma aplicação web desenvolvida para auxiliar produtores rurais no acompanhamento dos custos envolvidos no processo de engorda de bovinos.

O sistema permite registrar informações relacionadas à produção e aos custos da engorda, utilizando esses dados para calcular automaticamente o **custo por quilograma de carne produzido**.

A proposta é transformar dados da produção em informações mais fáceis de visualizar e utilizar para o acompanhamento da atividade pecuária.

---

## 🎯 Objetivo

O principal objetivo do projeto é desenvolver uma ferramenta simples e acessível para auxiliar no controle financeiro da engorda de bovinos.

### O sistema busca:

* 💰 Registrar os custos envolvidos na produção;
* 🐂 Registrar o peso inicial e o peso final;
* ⚖️ Calcular o ganho de peso;
* 🧮 Calcular automaticamente o custo por quilograma produzido;
* 📊 Facilitar a visualização das informações;
* 📈 Auxiliar no acompanhamento dos resultados da engorda.

---

## 🧮 Como funciona o cálculo?

O sistema utiliza o ganho de peso do animal para determinar o custo correspondente a cada quilograma produzido.

### 1. Ganho de peso

```text
Ganho de peso = Peso final − Peso inicial
```

### 2. Custo por quilograma

```text
Custo por kg = Custo total ÷ Ganho de peso
```

### 💡 Exemplo

Considerando:

```text
Custo total:  R$ 1.500,00
Peso inicial: 300 kg
Peso final:   450 kg
```

O ganho de peso será:

```text
450 − 300 = 150 kg
```

Portanto:

```text
R$ 1.500,00 ÷ 150 kg = R$ 10,00/kg
```

### Resultado:

> **Custo por quilograma produzido: R$ 10,00/kg**

---

## 🛠️ Tecnologias utilizadas

O projeto utiliza tecnologias voltadas para o desenvolvimento de aplicações web:

| Tecnologia      | Utilização                      |
| --------------- | ------------------------------- |
| 🐍 **Python**   | Linguagem principal             |
| 🌐 **Flask**    | Desenvolvimento do servidor web |
| 🗄️ **SQLite**  | Banco de dados                  |
| 🎨 **HTML**     | Estrutura das páginas           |
| 🎨 **CSS**      | Estilização da interface        |
| 🧩 **PlantUML** | Modelagem e documentação        |
| 🔧 **Git**      | Controle de versão              |
| 🐙 **GitHub**   | Hospedagem do código            |

---

## 📂 Estrutura do Projeto

```text
Gestao-de-Custos-da-Engorda/
│
├── 📁 src/
│   └── Código-fonte do projeto
│
├── 📁 static/
│   └── Arquivos estáticos
│       ├── CSS
│       ├── JavaScript
│       └── imagens
│
├── 📁 templates/
│   └── Páginas HTML da aplicação
│
├── 📄 app.py
│   └── Aplicação principal Flask
│
├── 📄 banco.db
│   └── Banco de dados SQLite
│
├── 📄 banco.puml
│   └── Diagrama do banco de dados
│
├── 📄 container.puml
│   └── Diagrama de contêiner
│
├── 📄 fluxo_calculo.puml
│   └── Fluxo do cálculo do custo
│
├── 📄 requirements.txt
│   └── Dependências do projeto
│
├── 📄 .gitignore
│   └── Arquivos ignorados pelo Git
│
└── 📄 README.md
    └── Documentação do projeto
```

---

## 🚀 Como executar o projeto

### 1️⃣ Clone o repositório

```bash
git clone https://github.com/gustavofagundes123/Gestao-de-Custos-da-Engorda.git
```

### 2️⃣ Entre na pasta

```bash
cd Gestao-de-Custos-da-Engorda
```

### 3️⃣ Crie um ambiente virtual

No Windows:

```bash
python -m venv venv
```

### 4️⃣ Ative o ambiente virtual

```bash
venv\Scripts\activate
```

### 5️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 6️⃣ Execute a aplicação

```bash
python app.py
```

### 7️⃣ Acesse no navegador

```text
http://127.0.0.1:5000
```

---

## 📊 Funcionalidades

### Atualmente

* [x] Aplicação web em Flask
* [x] Banco de dados SQLite
* [x] Estrutura de páginas HTML
* [x] Arquivos CSS/estáticos
* [x] Cálculo de custo por quilograma
* [x] Diagramas de modelagem
* [x] Controle de versão com Git/GitHub

### Em desenvolvimento

* [ ] Dashboard com indicadores
* [ ] Gráficos de custos
* [ ] Cadastro de diferentes categorias de custos
* [ ] Histórico de cálculos
* [ ] Relatórios
* [ ] Melhorias na experiência do usuário
* [ ] Sistema responsivo para dispositivos móveis

---

## 🧩 Modelagem do Sistema

O projeto possui diagramas desenvolvidos em **PlantUML** para representar diferentes aspectos da aplicação.

### 📌 Diagrama de Banco de Dados

Arquivo:

```text
banco.puml
```

Representa a estrutura e os relacionamentos utilizados no banco de dados.

### 📌 Diagrama de Contêiner

Arquivo:

```text
container.puml
```

Representa os principais componentes da aplicação e a comunicação entre eles.

### 📌 Fluxo do Cálculo

Arquivo:

```text
fluxo_calculo.puml
```

Representa o processo utilizado para chegar ao custo por quilograma produzido.

---

## 👨‍💻 Equipe

Projeto desenvolvido por alunos do:

**Instituto Federal de Educação, Ciência e Tecnologia de Rondônia — IFRO**

### Integrantes

* **Edy Henrique Machado Silva**
* **Luan da Cunha Martins**
* **Marcos Flavio Araujo Moreira**
* **Gustavo Fagundes de Araujo**

### Orientadora

**Eudoxia Lottie Silva Moura**

---

## 🎓 Contexto Acadêmico

Projeto desenvolvido no curso:

> **Técnico em Informática Integrado ao Ensino Médio**

O projeto tem como foco a aplicação prática de conceitos de:

* Engenharia de Software;
* Desenvolvimento Web;
* Banco de Dados;
* Programação;
* Modelagem de Sistemas;
* Controle de Versionamento;
* UI/UX.

---

## 📈 Possíveis melhorias futuras

O projeto poderá evoluir com a implementação de novas funcionalidades, como:

* 📊 Dashboard gerencial;
* 📈 Gráficos de desempenho;
* 🐄 Cadastro de animais e lotes;
* 💰 Categorias de custos;
* 📅 Histórico de produção;
* 📄 Geração de relatórios;
* 🔐 Sistema de usuários;
* 📱 Interface responsiva;
* ☁️ Disponibilização da aplicação na internet.

---

## 📄 Licença

Este projeto foi desenvolvido para fins **acadêmicos e educacionais**.

---

<div align="center">

### 🐂 Gestão de Custos da Engorda

**Transformando dados da produção em informações para a gestão.**

⭐ Desenvolvido com dedicação pelos alunos do IFRO.

</div>
