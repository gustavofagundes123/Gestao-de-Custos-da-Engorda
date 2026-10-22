# Gestão de Custos da Engorda

🌐 **Aplicação online:**  
[https://luanmartins1.pythonanywhere.com/](https://luanmartins1.pythonanywhere.com/)

## 📌 Sobre o projeto

O **Gestão de Custos da Engorda** é um sistema web desenvolvido para auxiliar no controle e gerenciamento dos custos relacionados à engorda de animais.

A aplicação permite cadastrar e gerenciar insumos, informar seus preços, registrar quantidades e unidades de medida e calcular o custo por quilograma produzido com base no ganho de peso dos animais.

O projeto foi desenvolvido como atividade prática do curso Técnico em Informática, utilizando Python, Flask, HTML, CSS e banco de dados SQLite.

## 🚀 Funcionalidades

- Cadastro de insumos;
- Listagem dos insumos cadastrados;
- Edição e exclusão de insumos;
- Registro da quantidade e unidade de medida;
- Cadastro do preço total da quantidade de cada insumo;
- Seleção de peso por saco, com opções de 15, 20, 25, 30, 35 ou 40 kg;
- Exibição do peso total dos insumos cadastrados em sacos;
- Atualização automática do custo total com base nos preços cadastrados;
- Cálculo do ganho de peso dos animais;
- Cálculo do custo por quilograma produzido;
- Armazenamento dos dados em banco de dados SQLite;
- Disponibilização da aplicação online pelo PythonAnywhere.

## 🧮 Como funciona o cálculo

O sistema soma os preços totais cadastrados para obter o custo dos insumos.

Em seguida, calcula o ganho de peso dos animais:

**Ganho de peso = Peso final − Peso inicial**

Por fim, calcula o custo por quilograma produzido:

**Custo por kg produzido = Custo total dos insumos ÷ Ganho de peso**

### Exemplo

Considerando os seguintes dados:

- Custo total dos insumos: R$ 500,00;
- Peso inicial dos animais: 300 kg;
- Peso final dos animais: 400 kg;
- Ganho de peso: 100 kg.

O custo por quilograma produzido será de **R$ 5,00/kg**.

## 🛠️ Tecnologias utilizadas

- Python;
- Flask;
- HTML5;
- CSS3;
- SQLite;
- PlantUML;
- Git e GitHub;
- PythonAnywhere.

## 🏗️ Arquitetura do projeto

O projeto utiliza uma aplicação web desenvolvida em Flask, responsável pelo processamento das requisições, validação dos dados e comunicação com o banco de dados SQLite.

A estrutura principal está organizada da seguinte forma:

```text
Gestao-de-Custos-da-Engorda/
│
├── app.py
├── banco.db
├── requirements.txt
├── README.md
│
├── src/
│   └── custo_engorda.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── cadastrar.html
│   └── editar.html
│
├── static/
│   └── style.css
│
├── banco.puml
├── container.puml
└── fluxo_calculo.puml
```

## 💻 Como executar o projeto localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/gustavofagundes123/Gestao-de-Custos-da-Engorda.git
```

### 2. Entrar na pasta do projeto

```bash
cd Gestao-de-Custos-da-Engorda
```

### 3. Criar um ambiente virtual

No Windows:

```bash
python -m venv venv
```

### 4. Ativar o ambiente virtual

No Windows, usando PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 6. Executar a aplicação

```bash
python app.py
```

A aplicação estará disponível localmente em:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🗄️ Banco de dados

O sistema utiliza SQLite para armazenar os insumos cadastrados.

Os registros incluem nome, quantidade, unidade de medida, preço total e peso por saco, quando aplicável.

A aplicação cria a tabela necessária e adiciona as novas colunas ao banco existente quando necessário, preservando os registros anteriores.

## 🌐 Hospedagem

A aplicação está hospedada no PythonAnywhere, permitindo o acesso pela internet.

**Acesse o sistema:**  
[https://luanmartins1.pythonanywhere.com/](https://luanmartins1.pythonanywhere.com/)

## 📚 Objetivo acadêmico

Este projeto tem como objetivo aplicar conhecimentos de desenvolvimento web, programação em Python, manipulação de banco de dados, organização de código e controle de versão com Git e GitHub.

A aplicação busca facilitar o acompanhamento dos custos dos insumos e apoiar a análise do custo por quilograma produzido durante a engorda de animais.

## 👨‍💻 Desenvolvimento

Projeto desenvolvido como atividade prática do curso Técnico em Informática.
