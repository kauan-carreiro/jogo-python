import pygame

from classes.constantes import (
    ALTURA_TELA,
    COR_AMARELO,
    COR_BRANCO,
    COR_CINZA,
    COR_CINZA_CLARO,
    COR_DESTAQUE,
    COR_VERMELHO,
    LARGURA_TELA,
    TECLA_TELA_CONTROLES,
)

# ── Paleta retro (espelha menu.py / tela_inicial.py) ──────────────────────────
_COR_FUNDO_OVERLAY = (8,   8,  20, 210)
_COR_AMARELO       = (255, 210,  0)
_COR_AMARELO_DIM   = (140, 110,  0)
_COR_P1            = (255, 215,  0)   # dourado — Player 1
_COR_P2            = (255,  80, 80)   # vermelho — Player 2

# Cor temática por letra de alternativa (igual às alternativas da batalha)
_CORES_LETRA = {
    "A": (255, 215,  0),   # dourado
    "B": (100, 200, 255),  # azul céu
    "C": (180, 100, 255),  # roxo
    "D": ( 80, 220, 120),  # verde
}


class TelaControles:
    """
    Overlay que exibe, de forma clara e organizada, quais teclas cada
    jogador deve usar para responder às alternativas (A, B, C, D).

    É exibida em dois momentos:
    - Automaticamente antes do início da primeira rodada de cada batalha.
    - Sob demanda, a qualquer momento da batalha, ao pressionar a tecla
      definida em TECLA_TELA_CONTROLES (F1).

    Em ambos os casos ela aparece por cima do jogo e congela o cronômetro
    e a contagem regressiva da rodada enquanto estiver aberta. Em qualquer
    caso, só é fechada quando o jogador pressiona TECLA_TELA_CONTROLES (F1)
    novamente.
    """

    def __init__(self, tela: pygame.Surface) -> None:
        self.tela = tela

        self.fonte_titulo      = pygame.font.SysFont("couriernew,courier,monospace", 34, bold=True)
        self.fonte_subtitulo   = pygame.font.SysFont("couriernew,courier,monospace", 13)
        self.fonte_nome_jogador = pygame.font.SysFont("segoe ui,arial,sans-serif",   22, bold=True)
        self.fonte_letra       = pygame.font.SysFont("segoe ui,arial,sans-serif",    20, bold=True)
        self.fonte_tecla       = pygame.font.SysFont("couriernew,courier,monospace", 18, bold=True)
        self.fonte_rodape      = pygame.font.SysFont("couriernew,courier,monospace", 13)

    def _desenhar_cartao_jogador(
        self,
        nome_jogador: str,
        teclas_em_ordem: list,
        cor_destaque: tuple,
        centro_x: int,
        topo_y: int,
    ) -> None:
        """Desenha o cartão com o mapeamento de alternativas -> tecla de um jogador."""
        largura_cartao = 320
        altura_cartao  = 300
        cartao = pygame.Rect(centro_x - largura_cartao // 2, topo_y, largura_cartao, altura_cartao)

        # Sombra pixel-art
        s_sombra = pygame.Surface(cartao.size, pygame.SRCALPHA)
        pygame.draw.rect(s_sombra, (0, 0, 0, 60), (4, 4, cartao.w, cartao.h), border_radius=6)
        self.tela.blit(s_sombra, cartao.topleft)

        # Corpo do cartão
        superficie = pygame.Surface(cartao.size, pygame.SRCALPHA)
        pygame.draw.rect(superficie, (12, 12, 30, 230), (0, 0, cartao.w, cartao.h), border_radius=6)
        # Barra lateral colorida (estilo card do menu)
        pygame.draw.rect(superficie, (*cor_destaque, 255), (0, 0, 5, cartao.h), border_radius=3)
        # Borda
        pygame.draw.rect(superficie, (*cor_destaque, 200), (0, 0, cartao.w, cartao.h), width=2, border_radius=6)
        self.tela.blit(superficie, cartao.topleft)

        # Nome do jogador
        texto_nome = self.fonte_nome_jogador.render(nome_jogador, True, cor_destaque)
        sombra_nome = self.fonte_nome_jogador.render(nome_jogador, True, (0, 0, 0))
        nx = cartao.centerx - texto_nome.get_width() // 2
        ny = cartao.y + 14
        self.tela.blit(sombra_nome, (nx + 1, ny + 1))
        self.tela.blit(texto_nome,  (nx, ny))

        # Linha separadora fina
        sep_y = ny + texto_nome.get_height() + 8
        pygame.draw.line(self.tela, (*cor_destaque, 120),
                         (cartao.x + 16, sep_y), (cartao.right - 16, sep_y), 1)

        letras      = ["A", "B", "C", "D"]
        altura_linha = 52
        y_inicial   = sep_y + 10

        for indice, letra in enumerate(letras):
            cor_letra = _CORES_LETRA[letra]
            y    = y_inicial + indice * (altura_linha + 6)
            linha = pygame.Rect(cartao.x + 12, y, largura_cartao - 24, altura_linha)

            # Fundo do item
            s_item = pygame.Surface(linha.size, pygame.SRCALPHA)
            pygame.draw.rect(s_item, (22, 22, 46, 160), (0, 0, linha.w, linha.h), border_radius=4)
            # Mini-barra lateral com a cor da letra
            pygame.draw.rect(s_item, (*cor_letra, 200), (0, 0, 4, linha.h), border_radius=2)
            pygame.draw.rect(s_item, (*cor_letra, 100), (0, 0, linha.w, linha.h), width=1, border_radius=4)
            self.tela.blit(s_item, linha.topleft)

            # Texto "Alternativa X"
            texto_letra = self.fonte_letra.render(f"Alternativa {letra}", True, COR_BRANCO)
            self.tela.blit(texto_letra, (linha.x + 14,
                                         linha.y + linha.h // 2 - texto_letra.get_height() // 2))

            # Badge da tecla
            nome_tecla = teclas_em_ordem[indice]
            self._desenhar_tecla(nome_tecla, linha.right - 12, linha.centery, cor_letra)

    def _desenhar_tecla(self, nome_tecla: str, borda_direita_x: int, centro_y: int, cor_destaque: tuple) -> None:
        """Desenha um badge retro representando a tecla física."""
        texto       = self.fonte_tecla.render(nome_tecla, True, cor_destaque)
        largura_botao = max(38, texto.get_width() + 18)
        altura_botao  = 30

        botao = pygame.Rect(0, 0, largura_botao, altura_botao)
        botao.right   = borda_direita_x
        botao.centery = centro_y

        s_botao = pygame.Surface(botao.size, pygame.SRCALPHA)
        pygame.draw.rect(s_botao, (*cor_destaque,  35), (0, 0, botao.w, botao.h), border_radius=4)
        pygame.draw.rect(s_botao, (*cor_destaque, 220), (0, 0, botao.w, botao.h), width=2, border_radius=4)
        self.tela.blit(s_botao, botao.topleft)

        self.tela.blit(texto, (botao.centerx - texto.get_width() // 2,
                               botao.centery - texto.get_height() // 2))

    def desenhar(self) -> None:
        """Desenha a tela de controles cobrindo toda a área de jogo."""
        # Fundo escurecido semitransparente (mantém o cenário visível ao fundo)
        fundo = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        fundo.fill(_COR_FUNDO_OVERLAY)
        self.tela.blit(fundo, (0, 0))

        # ── Título ────────────────────────────────────────────────────────────
        titulo_txt = "CONTROLES DA BATALHA"
        titulo  = self.fonte_titulo.render(titulo_txt, True, _COR_AMARELO)
        sombra_t = self.fonte_titulo.render(titulo_txt, True, (60, 40, 0))
        tx = LARGURA_TELA // 2 - titulo.get_width() // 2
        ty = 60
        self.tela.blit(sombra_t, (tx + 3, ty + 3))
        self.tela.blit(titulo,   (tx, ty))

        # Linha dupla decorativa (igual à tela_inicial.py)
        linha_y = ty + titulo.get_height() + 10
        meio    = LARGURA_TELA // 2
        pygame.draw.line(self.tela, _COR_AMARELO,     (meio - 280, linha_y),   (meio + 280, linha_y),   2)
        pygame.draw.line(self.tela, _COR_AMARELO_DIM, (meio - 200, linha_y+5), (meio + 200, linha_y+5), 1)

        # Subtítulo
        subtitulo = self.fonte_subtitulo.render(
            "Use as teclas abaixo para escolher a alternativa correta", True, (225, 225, 240)
        )
        self.tela.blit(subtitulo, (LARGURA_TELA // 2 - subtitulo.get_width() // 2, linha_y + 14))

        # ── Cartões dos dois jogadores ────────────────────────────────────────
        topo_cartoes = linha_y + 46
        self._desenhar_cartao_jogador(
            "PLAYER 1", ["Q", "W", "E", "R"], _COR_P1,
            LARGURA_TELA // 2 - 200, topo_cartoes,
        )
        self._desenhar_cartao_jogador(
            "PLAYER 2", ["U", "I", "O", "P"], _COR_P2,
            LARGURA_TELA // 2 + 200, topo_cartoes,
        )

        # ── Rodapé ────────────────────────────────────────────────────────────
        nome_tecla_overlay = pygame.key.name(TECLA_TELA_CONTROLES).upper()
        linha_1 = f"Pressione {nome_tecla_overlay} para fechar e continuar"
        linha_2 = f"Pressione {nome_tecla_overlay} novamente quando quiser ver os controles de novo"

        y_rodape = topo_cartoes + 300 + 18

        pygame.draw.line(self.tela, (40, 40, 65),
                         (LARGURA_TELA // 2 - 320, y_rodape - 8),
                         (LARGURA_TELA // 2 + 320, y_rodape - 8), 1)

        for indice, linha in enumerate((linha_1, linha_2)):
            partes = linha.split(nome_tecla_overlay)
            cx = LARGURA_TELA // 2 - self.fonte_rodape.size(linha)[0] // 2
            cy = y_rodape + indice * 22
            for i, parte in enumerate(partes):
                if parte:
                    sombra = self.fonte_rodape.render(parte, True, (0, 0, 0))
                    s = self.fonte_rodape.render(parte, True, (210, 210, 225))
                    self.tela.blit(sombra, (cx + 1, cy + 1))
                    self.tela.blit(s, (cx, cy))
                    cx += s.get_width()
                if i < len(partes) - 1:
                    sombra_key = self.fonte_rodape.render(nome_tecla_overlay, True, (0, 0, 0))
                    s_key = self.fonte_rodape.render(nome_tecla_overlay, True, _COR_AMARELO)
                    self.tela.blit(sombra_key, (cx + 1, cy + 1))
                    self.tela.blit(s_key, (cx, cy))
                    cx += s_key.get_width()