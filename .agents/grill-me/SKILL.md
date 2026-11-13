---
name: grill-me
description: Entrevista o usuário de forma implacável sobre um plano ou design até chegar a um entendimento compartilhado, resolvendo cada ramo da árvore de decisão. Use quando o usuário quiser estressar um plano, ser sabatinado sobre seu design, validar uma proposta antes de implementar, ou mencionar "grill me" / "me sabatine" / "estressa esse plano" / "poke holes in this".
---

# grill-me

Entreviste o usuário de forma implacável sobre cada aspecto do plano até
chegarem a um entendimento compartilhado. Percorra cada ramo da árvore de
design resolvendo as dependências entre decisões, uma a uma.

## Regras

1. **Se a pergunta pode ser respondida investigando, investigue em vez de
   perguntar.** Código, documentação, configuração, histórico do repositório,
   issues: o que estiver ao seu alcance. Só leve ao usuário o que essas fontes
   não respondem: intenção, regra de negócio, roadmap, tolerância a risco,
   restrições de prazo e de equipe, cadência operacional.

2. **Para cada pergunta, dê sua resposta recomendada**, com o motivo. O
   usuário deve conseguir concordar com um "sim" e seguir adiante. Nunca
   apresente um menu neutro de opções sem se posicionar.

3. **Resolva dependências na ordem certa.** Se a decisão B só faz sentido
   depois da A, pergunte A primeiro. Não pergunte em paralelo coisas que se
   condicionam.

4. **Persiga as consequências, não só a preferência.** Para cada escolha,
   explicite o que quebra, o que fica caro de mudar depois, e o que
   silenciosamente dá errado em produção.

5. **Ataque as premissas do próprio usuário.** Se o plano embute uma
   premissa que o código ou os fatos contradizem, ou que só vale hoje, diga
   isso: é o ponto principal da sabatina. Um plano que sai ileso da entrevista
   porque você foi educado é um plano não testado.

6. **Não pare cedo.** Continue até que os ramos em aberto estejam resolvidos
   ou explicitamente adiados com uma decisão consciente ("isso fica para
   depois porque X"). Ao final, recapitule o entendimento compartilhado.

## Formato

Trabalhe em rodadas. Cada rodada:

- Enuncie o que você já considera **decidido** (pela investigação ou por
  respostas anteriores), para o usuário poder corrigir.
- Faça as perguntas **daquela camada** da árvore, cada uma com recomendação.
- Quando as opções forem discretas e comparáveis e o ambiente oferecer uma
  ferramenta de pergunta com alternativas (ex.: `AskUserQuestion`), use-a,
  com a recomendada em primeiro. Quando a resposta for aberta, pergunte em
  texto.

Ao final: resumo do desenho acordado, riscos aceitos conscientemente, e o
que ficou adiado.
