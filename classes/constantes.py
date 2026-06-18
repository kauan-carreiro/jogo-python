import os

import pygame

# ===================== CONFIGURAÇÕES DE TELA =====================
LARGURA_TELA = 1024
ALTURA_TELA = 768
QUADROS_POR_SEGUNDO = 60
TITULO_JANELA = "Batalha do Conhecimento"

# ===================== CAMINHOS DE PASTAS =====================
PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_ASSETS = os.path.join(PASTA_RAIZ, "assets")
PASTA_PERSONAGENS = os.path.join(PASTA_ASSETS, "personagens")
PASTA_CENARIOS = os.path.join(PASTA_ASSETS, "cenarios")
PASTA_SONS = os.path.join(PASTA_ASSETS, "sons")
PASTA_DADOS = os.path.join(PASTA_RAIZ, "dados")
CAMINHO_PERGUNTAS = os.path.join(PASTA_DADOS, "perguntas.json")

# ===================== CORES (RGB) =====================
COR_BRANCO = (255, 255, 255)
COR_PRETO = (0, 0, 0)
COR_VERMELHO = (200, 40, 40)
COR_VERMELHO_CLARO = (240, 90, 90)
COR_VERDE = (40, 180, 90)
COR_AZUL = (40, 110, 200)
COR_AMARELO = (240, 200, 40)
COR_CINZA = (60, 60, 70)
COR_CINZA_CLARO = (150, 150, 160)
COR_FUNDO_PADRAO = (25, 25, 40)
COR_DESTAQUE = (255, 215, 0)

# ===================== MAPEAMENTO DE TECLAS =====================
# Player 1 utiliza Q, W, E, R para as alternativas A, B, C, D.
TECLAS_JOGADOR_1 = {
    pygame.K_q: "A",
    pygame.K_w: "B",
    pygame.K_e: "C",
    pygame.K_r: "D",
}

# Player 2 utiliza U, I, O, P para as alternativas A, B, C, D.
TECLAS_JOGADOR_2 = {
    pygame.K_u: "A",
    pygame.K_i: "B",
    pygame.K_o: "C",
    pygame.K_p: "D",
}

# Tecla que abre/fecha a tela de controles durante a batalha.
TECLA_TELA_CONTROLES = pygame.K_F1

# ===================== CONFIGURAÇÕES DE COMBATE =====================
VIDA_INICIAL = 100

# Tempo (em segundos) que os jogadores têm para responder após a leitura.
TEMPO_LIMITE_RESPOSTA = 8.0

# Pequeno atraso antes de habilitar as respostas, dando tempo de leitura.
TEMPO_LEITURA_PERGUNTA = 1.5

# Tempo que o resultado da rodada (dano, animações) fica exibido na tela.
TEMPO_EXIBICAO_RESULTADO_RODADA = 2.2

# Bônus de dano extra para quem acerta primeiro na rodada.
BONUS_PRIMEIRA_RESPOSTA_CORRETA = 3

# Número máximo de perguntas em uma batalha, mesmo que ninguém seja derrotado.
QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA = 20

# Tabela de dano: [dificuldade][faixa_de_tempo] = dano causado.
# A IA ajustou os valores originais para manter as partidas entre 3 e 8 minutos
# considerando o tempo de leitura, resposta e exibição de resultado de cada rodada.
TABELA_DANO = {
    "dificil": {"rapida": 18, "media": 15, "lenta": 10},
    "normal": {"rapida": 14, "media": 11, "lenta": 8},
    "facil": {"rapida": 10, "media": 8, "lenta": 5},
}

# Limites (em segundos) que definem cada faixa de velocidade de resposta.
FAIXA_TEMPO_RAPIDA = 2.0
FAIXA_TEMPO_MEDIA = 5.0

# ===================== ANIMAÇÃO =====================
INTERVALO_TROCA_QUADRO_IDLE = 0.35   # segundos entre cada quadro de idle
DURACAO_ANIMACAO_ATAQUE = 0.6
DURACAO_ANIMACAO_DANO = 0.5

# ===================== ESTADOS DO JOGO =====================
ESTADO_TELA_INICIAL = "tela_inicial"
ESTADO_HISTORIA = "historia"
ESTADO_MENU = "menu"
ESTADO_BATALHA = "batalha"
ESTADO_RESULTADO = "resultado"
ESTADO_CREDITOS = "creditos"

# ===================== MODOS DE JOGO =====================
MODO_MATEMATICA = "matematica"
MODO_PORTUGUES = "portugues"
MODO_MISTA = "mista"

# ===================== CONTAGEM REGRESSIVA =====================
TEMPO_CONTAGEM_REGRESSIVA = 1.0      # segundos entre cada número (3,2,1)
TEMPO_EXIBICAO_GO = 1.0              # segundos que "GO!" fica na tela

# ===================== MENSAGENS FLUTUANTES =====================
TEMPO_EXIBICAO_DANO = 1.5            # segundos que o dano fica visível

# ===================== ANIMAÇÃO DE ERRO =====================
# O nome do arquivo já está definido em gerenciador_animacoes.py