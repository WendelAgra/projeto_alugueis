# Sistema de Gestão de Aluguéis

![Banner do Projeto](image_2f498c.jpg)

## 📖 Sobre o Projeto

Este projeto é uma aplicação web **full-stack** completa para a gestão de aluguéis de imóveis, desenvolvida com Python e Flask. A plataforma permite que múltiplos utilizadores (locadores) se registem e administrem as suas propriedades, inquilinos e finanças de forma isolada e segura.

O sistema foi concebido para ser uma solução robusta e profissional, indo desde a gestão básica de dados até funcionalidades avançadas de automação, como a geração automática de cobranças mensais.

---

## ✨ Funcionalidades Principais

O sistema conta com um vasto conjunto de funcionalidades, incluindo:

### 🔑 Gestão e Segurança
* **Autenticação de Utilizadores:** Sistema seguro de registo e login.
* **Privacidade de Dados (Multi-Tenancy):** Cada utilizador só tem acesso aos seus próprios dados.
* **Gestão de Perfil:** Os utilizadores podem editar o seu nome de utilizador e alterar a sua senha.

### 🗂️ Módulos de Gestão (CRUD)
* **Gestão de Imóveis:** CRUD completo para adicionar, visualizar, editar e excluir casas/apartamentos.
* **Gestão de Inquilinos:** CRUD completo para a gestão de inquilinos.
* **Gestão de Contratos:** Secção dedicada para criar contratos com detalhes como valor, datas de início e fim, e dia de vencimento.

### 🤖 Automação e Inteligência
* **Geração Automática de Cobranças:** Com um único clique, o sistema gera todas as cobranças de aluguel pendentes para o mês atual com base nos contratos ativos.
* **Dashboard Financeiro:** A página inicial apresenta métricas importantes, como o total pendente e o total recebido no mês.
* **Relatório de Pendências:** Uma visão clara dos aluguéis atrasados e dos que estão prestes a vencer.

### 💻 Interface e Experiência do Utilizador (UX)
* **Design Moderno:** Interface com um design profissional, utilizando um tema de "vidro fosco" (*glassmorphism*) e gradientes.
* **Busca e Paginação:** Funcionalidade de busca global no dashboard e paginação em listas longas para uma navegação fluida.
* **Upload de Ficheiros:** Possibilidade de anexar documentos (PDF, imagens) a cada registo de aluguel.
* **Melhorias de UX:** Ícones visuais, feedback de "loading" em botões, animações suaves e a funcionalidade de mostrar/esconder senha.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias:

* **Backend:** Python 3, Flask
* **Frontend:** HTML5, CSS3, JavaScript
* **Banco de Dados:** SQLite 3
* **Bibliotecas Python Principais:**
    * `Flask`
    * `Flask-Login` (para autenticação)
    * `Werkzeug` (para hashing de senhas e segurança)

---

## 🚀 Como Executar o Projeto

Para executar este projeto localmente, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [https://seu-link-para-o-repositorio.git](https://seu-link-para-o-repositorio.git)
    cd projeto_alugueis2.0
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install Flask Flask-Login Werkzeug
    ```

4.  **Crie o banco de dados (apenas na primeira vez):**
    * (Certifique-se de que tem um ficheiro `models.py` que cria todas as tabelas necessárias).
    ```bash
    python models.py
    ```

5.  **Execute a aplicação:**
    ```bash
    flask run
    ```

A aplicação estará disponível em `http://127.0.0.1:5000`.

---

## 🖼️ Galeria

![Tela de Login](image_2f41e7.png)
*Tela de login com design profissional.*

![Dashboard Principal](image_2f3e65.png)
*Dashboard com métricas financeiras e listas de aluguéis.*

![Gestão de Contratos](image_b947bf.png)
*Página de gestão de contratos com a função de gerar cobranças.*

---

## 🧑‍💻 Autor

**Wendel Vinicius de Oliveira Agra**

* [LinkedIn](https://www.linkedin.com/in/wendel-vinicius-de-oliveira-agra-057863260/)
* [GitHub](https://github.com/Wende-l)
