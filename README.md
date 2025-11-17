# 🛒 PriceApp

<div align="center">

![Versão](https://img.shields.io/badge/version-v8.10.2-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![Database](https://img.shields.io/badge/Database-Supabase-green?logo=supabase)
![Hosting](https://img.shields.io/badge/Hosted%20on-Render-cyan?logo=render)

</div>

> Aplicação completa para gerenciar, comparar e otimizar preços de produtos de supermercados de forma colaborativa.

O **PriceApp** é uma aplicação web PWA (Progressive Web App) construída para rastrear a flutuação de preços de produtos, permitindo que uma comunidade de usuários (com Administradores) mantenha um banco de dados de preços atualizado.

O principal diferencial é seu sistema de **Lista de Compras Otimizada**, que calcula a combinação de produtos mais barata, buscando o menor preço de cada item em diferentes mercados.

---

## 📋 Tabela de Conteúdos

* [Principais Funcionalidades](#-principais-funcionalidades)
* [Como Funciona](#-como-funciona-fluxo-de-uso)
* [Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [Licença](#-licença)

---

## 🚀 Principais Funcionalidades

O PriceApp foi construído com um roadmap robusto, resultando nas seguintes funcionalidades:

### 📊 Gerenciamento e Comparação de Preços
* **CRUD Completo:** Administradores podem gerenciar Produtos, Supermercados e Marcas.
* **Histórico de Preços:** Cada registro de preço é salvo com data, criando um histórico de flutuação.
* **Gráficos de Flutuação:** Visualização gráfica (usando Chart.js) da mudança de preço de um item ao longo do tempo.
* **Filtros de Busca:** Todos os formulários de registro (sugerir, registrar, editar) possuem filtros de texto para encontrar itens em listas longas.
* **Páginas por Mercado:** Visualização de todos os produtos que possuem preços cadastrados em um supermercado específico.

### 💰 Sistema de Promoções Avançado
* **Promoções por Tempo:** Capacidade de registrar promoções com data de validade.
* **Tipos de Promoção:** Suporte para dois tipos de promoção:
    1.  **Preço Reduzido:** (Ex: De R$ 5,00 por R$ 3,99).
    2.  **Por Quantidade:** (Ex: 3 unidades por R$ 10,00).
* **Card de Desconto:** A página de histórico exibe um card de destaque para promoções ativas, mostrando o valor do desconto.

### 🛒 Listas de Compras Inteligentes
* **Criação de Listas:** Usuários podem criar e gerenciar múltiplas listas de compras (Ex: "Compras da Semana", "Churrasco").
* **Otimização Multi-Mercado:** Ao comparar uma lista, o sistema **não** calcula o total por mercado. Em vez disso, ele cria uma **lista otimizada**, item por item, indicando qual mercado tem o menor preço para *cada produto individualmente*.
* **Cálculo de Promoção:** O comparador de listas leva em conta as promoções por quantidade para calcular o custo total real com base na quantidade desejada pelo usuário.

### 👥 Colaboração e Papéis de Usuário
* **Autenticação Completa:** Sistema de registro e login.
* **Divisão de Papéis (Admin/User):**
    * **Admins:** Têm controle total, aprovam sugestões e gerenciam o banco de dados.
    * **Usuários:** Podem ver preços, criar listas e, o mais importante, *colaborar* com sugestões.
* **Sistema de Sugestão de Preços:** Usuários comuns podem enviar novos preços (incluindo promoções) para a aprovação de um Admin.
* **Sistema de Sugestão de Edição:** Usuários comuns podem sugerir correções para nomes de Produtos, Marcas ou endereços de Mercados.
* **Auditoria de Dados:** O sistema rastreia qual usuário (seja por registro direto ou sugestão aprovada) cadastrou cada preço.

### 📱 PWA e Utilitários de Dados
* **Design Responsivo (PWA):** O layout é adaptado para uso mobile e desktop, funcionando como um Progressive Web App.
* **Sincronização Offline:** Um botão permite ao usuário baixar o banco de dados JSON no `localStorage` do navegador.
* **Leitor Offline:** Uma página dedicada (`/leitor-offline`) acessa os dados sincronizados, permitindo a consulta de preços e históricos mesmo sem internet.
* **Backup em Excel:** Administradores podem baixar um backup completo do banco de dados em formato `.xlsx` (Excel).

---

## ⚙️ Como Funciona (Fluxo de Uso)

1.  **Admin** cadastra os Itens base (Produtos, Mercados, Marcas).
2.  **Admin** (ou um **Usuário** via sugestão) registra um Preço para um item, informando se é uma promoção e sua validade.
3.  Um **Usuário** cria uma `Lista de Compras`.
4.  Ele adiciona "Arroz (5kg)", "Feijão (1kg)" e "Refrigerante (6 unidades)" à sua lista.
5.  Ao clicar em "Comparar", o PriceApp:
    * Verifica o melhor preço para "Arroz" (Ex: R$ 25,00 no Mercado A).
    * Verifica o melhor preço para "Feijão" (Ex: R$ 7,00 no Mercado B).
    * Verifica o "Refrigerante" e encontra uma promoção "6 por R$ 20,00" no Mercado A.
6.  O app exibe a lista otimizada, mostrando o custo total (R$ 52,00) e onde comprar cada item para obter a economia máxima.

---

## 💻 Tecnologias Utilizadas

* **Backend:** Python, Flask, Gunicorn
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Chart.js
* **Database:** Supabase (PostgreSQL)
* **Deployment:** Render
* **Principais Bibliotecas Python:**
    * `Flask-SQLAlchemy` (ORM)
    * `Flask-Login` (Autenticação)
    * `Flask-Bcrypt` (Hashing de Senhas)
    * `openpyxl` (Geração de Excel)

---

## 📄 Licença

Este projeto está licenciado sob a licença **LICENSE MIT**. Veja o arquivo [LICENSE](https://github.com/MestreUDK/PriceApp/blob/main/LICENSE) para mais detalhes.