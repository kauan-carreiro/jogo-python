import math
import os
import random

import pygame

from classes.constantes import (
    ALTURA_TELA,
    COR_BRANCO,
    COR_DESTAQUE,
    COR_FUNDO_PADRAO,
    LARGURA_TELA,
    PASTA_ASSETS,
)

INTERVALO_PISCAR_INSTRUCAO = 0.6

COR_FUNDO        = (12, 12, 28)        # quase preto azulado
COR_GRID         = (30, 30, 60)        # grade sutil
COR_AMARELO      = (255, 210, 0)       # amarelo MonitorAê
COR_INSTRUCAO    = (220, 220, 240)
COR_RODAPE       = (100, 100, 130)

# Tamanho do bloco da grade pixel
GRID_SIZE = 32


class TelaInicial:
    """Tela inicial estilo pixel-art clean. Fundo com grade de pontos animada
    e logo/título centralizados na tela."""

    def __init__(self, tela: pygame.Surface) -> None:
        self.tela = tela
        self.tempo_total: float = 0.0
        self.cronometro_piscar: float = 0.0

        # Fontes
        self.fonte_titulo  = pygame.font.SysFont("segoe ui", 72, bold=True)
        self.fonte_inst    = pygame.font.SysFont("segoe ui", 22, italic=True)
        self.fonte_rodape  = pygame.font.SysFont("segoe ui", 13)

        # Pré-renderiza a grade (pontos mudam de alpha com o tempo)
        self._pontos_grade = self._gerar_pontos_grade()

        # Carrega a logo (se existir)
        self.logo = self._carregar_logo()

        # Calcula onde cada elemento (logo / título / instrução) vai ficar,
        # como um bloco único centralizado, para nunca se sobreporem.
        self._calcular_layout()

    # ------------------------------------------------------------------ #

    def _gerar_pontos_grade(self):
        """Retorna lista de (x, y, fase) para os pontos da grade."""
        pontos = []
        for x in range(0, LARGURA_TELA + GRID_SIZE, GRID_SIZE):
            for y in range(0, ALTURA_TELA + GRID_SIZE, GRID_SIZE):
                fase = random.uniform(0, math.pi * 2)
                pontos.append((x, y, fase))
        return pontos

    def _carregar_logo(self) -> pygame.Surface | None:
        """Tenta carregar a logo de assets/imagens/logo.png."""
        caminho_logo = os.path.join(PASTA_ASSETS, "imagens", "logo.png")
        if os.path.isfile(caminho_logo):
            try:
                imagem = pygame.image.load(caminho_logo).convert_alpha()
                largura_max = 400
                proporcao = largura_max / imagem.get_width()
                nova_largura = int(imagem.get_width() * proporcao)
                nova_altura = int(imagem.get_height() * proporcao)
                return pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))
            except pygame.error:
                print("[AVISO] Não foi possível carregar a logo. Usando fallback textual.")
        return None

    def _calcular_layout(self) -> None:
        """Define as posições verticais de logo, título e instrução como um
        bloco único centralizado na tela, evitando qualquer sobreposição."""
        altura_logo = self.logo.get_height() if self.logo is not None else 0
        espaco_logo_titulo = 30 if self.logo is not None else 0
        altura_titulo = self.fonte_titulo.get_height()
        espaco_titulo_instrucao = 40
        altura_instrucao = self.fonte_inst.get_height()

        altura_bloco = (
            altura_logo + espaco_logo_titulo + altura_titulo
            + espaco_titulo_instrucao + altura_instrucao
        )

        topo = (ALTURA_TELA - altura_bloco) // 2

        self.logo_y = topo
        self.titulo_y = topo + altura_logo + espaco_logo_titulo
        self.instrucao_y = self.titulo_y + altura_titulo + espaco_titulo_instrucao

    # ------------------------------------------------------------------ #

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        return evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)

    def atualizar(self, tempo_decorrido: float) -> None:
        self.tempo_total += tempo_decorrido
        self.cronometro_piscar += tempo_decorrido

    def _desenhar_logo(self) -> None:
        if self.logo is not None:
            logo_x = (LARGURA_TELA - self.logo.get_width()) // 2
            self.tela.blit(self.logo, (logo_x, self.logo_y))

    def desenhar(self) -> None:
        self.tela.fill(COR_FUNDO)
        self._desenhar_grade()
        self._desenhar_scanlines_fundo()
        self._desenhar_logo()
        self._desenhar_titulo()
        self._desenhar_instrucao()
        self._desenhar_rodape()


    # ------------------------------------------------------------------ #

    def _desenhar_grade(self) -> None:
        """Grade de pontos com pulsação lenta — clean e retro."""
        for (x, y, fase) in self._pontos_grade:
            alpha = int(25 + 20 * math.sin(self.tempo_total * 0.8 + fase))
            surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            surf.fill((80, 80, 160, alpha))
            self.tela.blit(surf, (x - 1, y - 1))

    def _desenhar_scanlines_fundo(self) -> None:
        """Linhas horizontais finas para dar textura CRT retro ao fundo."""
        for y in range(0, ALTURA_TELA, 4):
            surf = pygame.Surface((LARGURA_TELA, 1), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 30))
            self.tela.blit(surf, (0, y))

    def _desenhar_titulo(self) -> None:
        """'Monitor' em branco + 'Aê - Game' em amarelo, com leve glitch horizontal."""
        parte1 = self.fonte_titulo.render("Monitor", True, COR_BRANCO)
        parte2 = self.fonte_titulo.render("Aê - Game", True, COR_AMARELO)

        total_w = parte1.get_width() + parte2.get_width()
        base_x  = LARGURA_TELA // 2 - total_w // 2
        base_y  = self.titulo_y

        # Sombra sólida deslocada (look pixel-art)
        sombra1 = self.fonte_titulo.render("Monitor", True, (60, 40, 0))
        sombra2 = self.fonte_titulo.render("Aê - Game", True, (40, 40, 40))
        self.tela.blit(sombra1, (base_x + 3, base_y + 3))
        self.tela.blit(sombra2, (base_x + parte1.get_width() + 3, base_y + 3))

        # Glitch: a cada ~3s desloca o título 1-2px por 1 frame
        glitch_x = 0
        if 0.02 > (self.tempo_total % 3.1) % 0.08:
            glitch_x = random.choice([-2, -1, 1, 2])

        self.tela.blit(parte1, (base_x + glitch_x, base_y))
        self.tela.blit(parte2, (base_x + parte1.get_width() + glitch_x, base_y))

    def _desenhar_instrucao(self) -> None:
        visivel = (self.cronometro_piscar % (INTERVALO_PISCAR_INSTRUCAO * 2)) < INTERVALO_PISCAR_INSTRUCAO
        if visivel:
            texto = self.fonte_inst.render("[ Pressione qualquer tecla para comecar ]", True, COR_INSTRUCAO)
            self.tela.blit(texto, (LARGURA_TELA // 2 - texto.get_width() // 2, self.instrucao_y))

    def _desenhar_rodape(self) -> None:
        texto = self.fonte_rodape.render(
            "Matematica  *  Portugues  *  Um projeto MonitorAe", True, COR_RODAPE
        )
        self.tela.blit(texto, (LARGURA_TELA // 2 - texto.get_width() // 2, ALTURA_TELA - 38))