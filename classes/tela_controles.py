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

        self.fonte_titulo = pygame.font.SysFont("segoe ui", 40, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("segoe ui", 20)
        self.fonte_nome_jogador = pygame.font.SysFont("segoe ui", 26, bold=True)
        self.fonte_letra = pygame.font.SysFont("segoe ui", 22, bold=True)
        self.fonte_tecla = pygame.font.SysFont("segoe ui", 26, bold=True)
        self.fonte_rodape = pygame.font.SysFont("segoe ui", 18)

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
        altura_cartao = 300
        cartao = pygame.Rect(centro_x - largura_cartao // 2, topo_y, largura_cartao, altura_cartao)

        superficie = pygame.Surface(cartao.size, pygame.SRCALPHA)
        superficie.fill((20, 20, 35, 235))
        self.tela.blit(superficie, cartao.topleft)
        pygame.draw.rect(self.tela, cor_destaque, cartao, width=3, border_radius=14)

        # Nome do jogador centralizado no topo do cartão
        texto_nome = self.fonte_nome_jogador.render(nome_jogador, True, cor_destaque)
        self.tela.blit(
            texto_nome,
            (cartao.centerx - texto_nome.get_width() // 2, cartao.y + 14),
        )

        letras = ["A", "B", "C", "D"]
        altura_linha = 56
        y_inicial = cartao.y + 64

        for indice, letra in enumerate(letras):
            y = y_inicial + indice * altura_linha
            linha = pygame.Rect(cartao.x + 16, y, largura_cartao - 32, altura_linha - 10)
            pygame.draw.rect(self.tela, COR_CINZA, linha, border_radius=10)
            pygame.draw.rect(self.tela, COR_CINZA_CLARO, linha, width=1, border_radius=10)

            texto_letra = self.fonte_letra.render(f"Alternativa {letra}", True, COR_BRANCO)
            self.tela.blit(texto_letra, (linha.x + 12, linha.y + linha.height // 2 - texto_letra.get_height() // 2))

            nome_tecla = teclas_em_ordem[indice]
            self._desenhar_tecla(nome_tecla, linha.right - 14, linha.centery, cor_destaque)

    def _desenhar_tecla(self, nome_tecla: str, borda_direita_x: int, centro_y: int, cor_destaque: tuple) -> None:
        """Desenha um pequeno 'botão' representando a tecla física do teclado."""
        texto = self.fonte_tecla.render(nome_tecla, True, COR_BRANCO)
        largura_botao = max(38, texto.get_width() + 20)
        altura_botao = 34

        botao = pygame.Rect(0, 0, largura_botao, altura_botao)
        botao.right = borda_direita_x
        botao.centery = centro_y

        pygame.draw.rect(self.tela, (35, 35, 50), botao, border_radius=8)
        pygame.draw.rect(self.tela, cor_destaque, botao, width=2, border_radius=8)
        self.tela.blit(texto, (botao.centerx - texto.get_width() // 2, botao.centery - texto.get_height() // 2))

    def desenhar(self) -> None:
        """Desenha a tela de controles cobrindo toda a área de jogo."""
        # Fundo escurecido cobrindo toda a tela, para destacar o overlay.
        fundo = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 190))
        self.tela.blit(fundo, (0, 0))

        # Título
        titulo = self.fonte_titulo.render("CONTROLES DA BATALHA", True, COR_DESTAQUE)
        self.tela.blit(titulo, (LARGURA_TELA // 2 - titulo.get_width() // 2, 70))

        subtitulo = self.fonte_subtitulo.render(
            "Use as teclas abaixo para escolher a alternativa correta", True, COR_BRANCO
        )
        self.tela.blit(subtitulo, (LARGURA_TELA // 2 - subtitulo.get_width() // 2, 122))

        # Cartões dos dois jogadores, lado a lado
        topo_cartoes = 170
        self._desenhar_cartao_jogador(
            "PLAYER 1",
            ["Q", "W", "E", "R"],
            COR_AMARELO,
            LARGURA_TELA // 2 - 200,
            topo_cartoes,
        )
        self._desenhar_cartao_jogador(
            "PLAYER 2",
            ["U", "I", "O", "P"],
            COR_VERMELHO,
            LARGURA_TELA // 2 + 200,
            topo_cartoes,
        )

        # Rodapé com a instrução de como fechar a tela (e reabri-la depois).
        # Duas linhas curtas em vez de uma única linha longa, para não
        # ultrapassar a largura da tela.
        nome_tecla_overlay = pygame.key.name(TECLA_TELA_CONTROLES).upper()
        linha_1 = f"Pressione {nome_tecla_overlay} para fechar e continuar"
        linha_2 = f"Pressione {nome_tecla_overlay} novamente quando quiser ver os controles de novo"

        y_rodape = topo_cartoes + 300 + 20
        for indice, linha in enumerate((linha_1, linha_2)):
            texto_linha = self.fonte_rodape.render(linha, True, COR_CINZA_CLARO)
            self.tela.blit(
                texto_linha,
                (LARGURA_TELA // 2 - texto_linha.get_width() // 2, y_rodape + indice * 24),
            )