# Fundamentos de segurança (AppSec)

Contexto sobre segurança de aplicações para o agente atuar como mentor de cibersegurança. Serve de base para conversas sobre vulnerabilidades, análise de risco e desenvolvimento seguro.

Segurança não é uma etapa do final do projeto: é uma forma de pensar cada decisão de código. O agente deve ensinar esse raciocínio, não apenas apontar "erros".

## Vulnerabilidade, ameaça e risco

Esses três termos parecem sinônimos, mas representam coisas diferentes. Confundir os três é o erro mais comum de quem está começando.

| Conceito | Definição | Exemplo | Pergunta que responde |
|----------|-----------|---------|-----------------------|
| **Vulnerabilidade** | Uma fraqueza no sistema (código, configuração, processo ou pessoa) que pode ser explorada. É um defeito. | A consulta SQL do `app.py` montada por concatenação de strings. | "O que está errado no meu sistema?" |
| **Ameaça** | Alguém ou algo com capacidade e intenção de explorar a fraqueza. Existe independentemente do seu código. | Um invasor automatizado que varre a internet procurando formulários de login. | "Quem ou o que pode me atacar?" |
| **Risco** | A combinação de probabilidade e impacto. É o que você gerencia com prioridade. | Alta probabilidade de ataque automatizado + alto impacto (acesso como `admin`) = risco alto. | "Quanta falta me faz resolver isso, e quando?" |

> ℹ️ O termo **agente de ameaça** (ou *threat actor*) é quem realiza a ameaça: um atacante humano, um grupo organizado, um script automatizado ou até um erro de operação.

Regra de ouro para o agente: **um fato não é um risco.** "Existe uma concatenação de string" é uma vulnerabilidade. O risco depende do contexto: o que aquela consulta protege, quem alcança esse código, qual o impacto se falhar e quão fácil é explorar.

### Fórmula simples de risco

```
Risco = Probabilidade x Impacto
```

- **Probabilidade:** quão fácil é explorar e quão exposto está o componente. Um login público é muito mais exposto que um script interno que roda uma vez por mês.
- **Impacto:** o que se perde se a falha for explorada. Vazamento de dados pessoais, perda de dinheiro, indisponibilidade, dano à reputação, obrigação legal (LGPD).

### Escala de severidade (referência prática)

| Severidade | Pista de contexto | Exemplo típico |
|------------|-------------------|----------------|
| **Crítica** | Explorável de fora, sem autenticação, leva a controle total ou vazamento massivo de dados sensíveis. | SQL Injection em login público que permite entrar como administrador. |
| **Alta** | Explorável de fora, exige alguma condição, impacto sério em dados ou em privilégios. | Injeção em uma tela autenticada que expõe dados de outros usuários. |
| **Média** | Exige interação da vítima, privilégios altos ou exposição limitada. | Falha que só funciona com um usuário já logado e revela pouca informação. |
| **Baixa** | Difícil de explorar ou de impacto pequeno. | Mensagem de erro que revela detalhe interno sem consequência prática. |

O agente deve sempre deixar claro que essa é uma **estimativa de mentor**, baseada nas respostas do estudante, e não um laudo formal. Uma análise oficial usa metodologias como CVSS e o julgamento de um profissional responsável.

## Tríade CIA

A tríade CIA (do inglês *Confidentiality, Integrity, Availability*) é o jeito clássico de olhar o que a segurança protege. Toda falha, no fundo, ataca pelo menos um desses três pilares.

### Confidencialidade (C)

**Só quem tem permissão consegue ver a informação.**

- O que protege: dados pessoais, senhas, dados financeiros, segredos de negócio, chaves de API.
- Como se quebra: SQL Injection que lista dados de outros usuários, IDOR (trocar o ID na URL e ver o dado de outra pessoa), log que grava senha em texto puro, `.env` commitado no Git.
- Como se protege: controle de acesso por recurso, princípio do menor privilégio, criptografia de dados sensíveis, nunca logar segredos.

### Integridade (I)

**A informação está correta e só foi alterada por quem podia alterar.**

- O que protege: registros, valores, histórico de transações, configurações.
- Como se quebra: injeção que permite `UPDATE`/`DELETE` indevido, ausência de validação de entrada, upload de arquivo sem verificação, falta de assinatura em mensagens entre sistemas.
- Como se protege: validação de entrada, transações no banco, permissões de escrita restritas, hashes e assinaturas para verificação.

### Disponibilidade (A)

**O sistema está no ar e respondendo quando é preciso.**

- O que protege: o acesso ao serviço em si.
- Como se quebra: negação de serviço (DoS), consulta SQL pesada disparada por injeção, falta de backup, ausência de limite de tentativas de login.
- Como se protege: limites de requisição (rate limiting), timeouts, backup testado, arquitetura resiliente.

### Como o agente usa a tríade

Ao analisar uma falha, pergunte ao estudante: **qual pilar (ou pilares) essa falha ataca e por quê?** Isso obriga a raciocinar sobre impacto em vez de decorar nomes de ataques.

Exemplo com o `app.py` do laboratório: uma injeção no login quebra a **Confidencialidade** (acesso a dados de outros usuários e do admin) e a **Integridade** (o invasor pode, a partir daí, alterar dados como um usuário legítimo). A **Disponibilidade** só entra em jogo se a injeção for usada para degradar o banco.

## Boas práticas defensivas de desenvolvimento seguro

Estas práticas são a base de qualquer conversa sobre correção. O agente deve explicar **o porquê** de cada uma, não apenas listar.

### 1. Nunca misture comando com dado (parametrização)

Este é o ponto central para injeção de SQL. Consultas parametrizadas (placeholders) enviam o comando e os valores por caminhos separados, então o banco trata a entrada sempre como dado, nunca como comando.

```python
# Errado: a entrada vira parte do comando
cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")

# Certo: a entrada é sempre dado, o comando é fixo
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

O mesmo raciocínio vale para outras injeções: comandos de sistema, LDAP, XSS (onde o "comando" é HTML/JavaScript) e templates.

### 2. Valide a entrada e codifique a saída

- **Validar a entrada:** aceite apenas o formato esperado (tipo, tamanho, caracteres permitidos, faixa de valores). Validação é uma camada a mais, não substitui a parametrização.
- **Codificar a saída:** ao renderizar dados em HTML, SQL, logs ou terminal, escape conforme o contexto. É assim que se evita XSS e injeção de log.

### 3. Princípio do menor privilégio

Cada parte do sistema deve ter só a permissão necessária para funcionar.

- O usuário de banco da aplicação não precisa ser `sa`/`root`.
- O código que só lê não deve ter permissão de escrita.
- Um endpoint só deve retornar os dados daquele usuário, nunca da tabela inteira.

### 4. Falhe de forma segura

Erros devem ser úteis para quem opera e inofensivos para quem ataca.

- Não mostre stack trace, SQL ou nome de tabela para o usuário final.
- Não informe "usuário existe, senha errada": use uma mensagem genérica no login.
- Registre o erro detalhado no log interno, sem dados sensíveis.

### 5. Senhas e segredos

- Nunca guarde senha em texto puro: use hash lento com salt (ex.: `bcrypt`, `argon2`, `scrypt`).
- Nunca coloque segredos no código ou no Git: use variáveis de ambiente (`.env` fora do versionamento).
- Autenticação não é autorização: quem está logado não tem acesso a tudo. Verifique permissão em cada recurso.

### 6. Dependências e configuração

- Mantenha bibliotecas atualizadas e remova o que não usa.
- Não deixe recursos de desenvolvimento ligados em produção (modo debug, CORS aberto, banco sem senha).
- Desative detalhes internos expostos por padrão (listagem de diretório, headers com versão, mensagens de depuração).

### 7. Verifique com mentalidade de ataque

- Revise o próprio código perguntando "como eu quebraria isso?".
- Teste apenas em ambiente autorizado e com dados fictícios.
- Use ferramentas de análise estática (SAST) e de dependências no pipeline de CI.
- Prefira padrões reconhecidos: OWASP Top 10, OWASP ASVS (checklist de verificação), CWE (catálogo de fraquezas) e as boas práticas da stack.

## Segurança de laboratório (importante)

Para estudar segurança, é essencial separar o que é **estudo** do que é **produção**:

- Rode código vulnerável apenas na sua máquina, com dados fictícios, e mantenha o repositório claramente marcado como laboratório.
- Nunca teste técnicas de ataque em sistemas de terceiros, mesmo "só para ver". Isso é ilegal e não é aprendizado.
- Após entender a falha, **escreva a correção e o teste que prova que ela não volta**. Esse é o objetivo final do estudo.

O `app.py` na raiz deste repositório é exatamente esse tipo de laboratório: um login em Python com `sqlite3` que tem SQL Injection proposital, feito para ser analisado e corrigido. Ele usa três usuários fictícios (`ana`, `bruno` e `admin`) e expõe um SQL de depuração no terminal, o que ajuda a estudante ver a consulta que o banco recebeu.

## Como o agente usa esta base

1. Use os conceitos de **vulnerabilidade, ameaça e risco** para ajudar o estudante a descrever o problema com precisão.
2. Use a **tríade CIA** para identificar o impacto.
3. Use as **boas práticas defensivas** para orientar a correção, sempre explicando o motivo.
4. Nunca entregue payload completo de ataque nem correção pronta: conduza com a skill `vulnerability-analysis`.

