# Platformer Game

## Descrição

Este é um jogo de plataforma simples feito com PgZero. O jogador deve derrotar todos os inimigos presentes no mapa para vencer.

## Como rodar

1. Clone o repositório:

   ```bash
   git clone https://github.com/RodrigoSilvaPereira/PgZeroGame.git
   cd PgZeroGame
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / Mac
   source venv/bin/activate
   ```

3. Instale o PgZero:

   ```bash
   pip install -r "requirements.txt"
   ```

4. Execute o jogo:

   ```bash
   pgzrun main.py
   ```

## Controles

* **A**: Mover para a esquerda
* **D**: Mover para a direita
* **W**: Pular
* **SPACE**: Atacar / iniciar jogo no menu
* **Clique nos botões do menu** para iniciar, ligar/desligar música ou sair

## Observações

* O jogo é feito apenas com PgZero, math e random.
* Nenhuma outra biblioteca é necessária.
* Mantenha as imagens e arquivos de som na mesma pasta do `main.py`.
