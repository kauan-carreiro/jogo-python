from typing import List, Optional, TYPE_CHECKING
import math
import random

import pygame

if TYPE_CHECKING:
    from classes.gerenciador_sons import GerenciadorSons

from classes.constantes import (
    ALTURA_TELA,
    COR_BRANCO,
    COR_CINZA_CLARO,
    COR_DESTAQUE,
    COR_FUNDO_PADRAO,
    LARGURA_TELA,
)

OPCOES_MENU: List[str] = [
    "Batalha Matemática",
    "Batalha Português",
    "Batalha Mista",
    "Sair",
]

ICONES_MENU = ["∑", "Aa", "⚔", "✕"]

CORES_OPCAO = [
    (255, 215,   0),   # Matemática — dourado
    (100, 200, 255),   # Português  — azul céu
    (180, 100, 255),   # Mista      — roxo
    (200,  70,  70),   # Sair       — vermelho
]

# ── Paleta (espelhando tela_inicial.py) ──────────────────────────────────────
COR_FUNDO       = (12, 12, 28)
COR_AMARELO     = (255, 210,  0)
COR_AMARELO_DIM = (140, 110,  0)
GRID_SIZE       = 32

INTERVALO_PISCAR = 0.5


class Menu:
    """Menu principal — fundo grid/scanlines idêntico à tela inicial."""

    def __init__(self, tela: pygame.Surface, gerenciador_sons: "GerenciadorSons") -> None:
        self.tela = tela
        self.gerenciador_sons = gerenciador_sons

        self.fonte_titulo_bold   = pygame.font.SysFont("couriernew,courier,monospace", 54, bold=True)
        self.fonte_opcao         = pygame.font.SysFont("segoe ui,arial,sans-serif",    28, bold=True)
        self.fonte_icone         = pygame.font.SysFont("segoe ui symbol,arial unicode ms", 20, bold=True)
        self.fonte_ajuda         = pygame.font.SysFont("couriernew,courier,monospace", 13)
        self.fonte_numero        = pygame.font.SysFont("couriernew,courier,monospace", 11, bold=True)

        self.indice_opcao_selecionada = 0
        self.cronometro_piscar        = 0.0
        self.cursor_visivel           = True
        self.offset_hover             = [0.0] * len(OPCOES_MENU)
        self.tempo_total              = 0.0

        # Pré-gera pontos da grade (igual à tela_inicial)
        self._pontos_grade = [
            (x, y, random.uniform(0, math.pi * 2))
            for x in range(0, LARGURA_TELA + GRID_SIZE, GRID_SIZE)
            for y in range(0, ALTURA_TELA  + GRID_SIZE, GRID_SIZE)
        ]

    # ── Fundo ────────────────────────────────────────────────────────────────

    def _desenhar_fundo(self) -> None:
        self.tela.fill(COR_FUNDO)

        # Grade de pontos pulsantes (idêntico à tela_inicial)
        for (x, y, fase) in self._pontos_grade:
            alpha = int(25 + 20 * math.sin(self.tempo_total * 0.8 + fase))
            surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            surf.fill((80, 80, 160, alpha))
            self.tela.blit(surf, (x - 1, y - 1))

        # Scanlines CRT (idêntico à tela_inicial)
        for y in range(0, ALTURA_TELA, 4):
            surf = pygame.Surface((LARGURA_TELA, 1), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 30))
            self.tela.blit(surf, (0, y))

    # ── Título ───────────────────────────────────────────────────────────────

    def _desenhar_titulo(self) -> None:
        parte1 = "Monitor"
        parte2 = "Aê - Game"

        t1 = self.fonte_titulo_bold.render(parte1, True, COR_BRANCO)
        t2 = self.fonte_titulo_bold.render(parte2, True, COR_AMARELO)

        largura_total = t1.get_width() + t2.get_width()
        pos_y = 52

        # Sombra sólida pixel-art (sem blur) + texto, parte a parte
        px = (LARGURA_TELA - largura_total) // 2
        for txt, nome, cor_sombra in [(t1, parte1, (60, 40, 0)), (t2, parte2, (40, 40, 40))]:
            sombra = self.fonte_titulo_bold.render(nome, True, cor_sombra)
            self.tela.blit(sombra, (px + 3, pos_y + 3))
            self.tela.blit(txt,    (px,     pos_y))
            px += txt.get_width()

        # Linha dupla decorativa (igual à tela_inicial)
        linha_y = pos_y + t1.get_height() + 10
        meio = LARGURA_TELA // 2
        pygame.draw.line(self.tela, COR_AMARELO,     (meio-240, linha_y),   (meio+240, linha_y),   2)
        pygame.draw.line(self.tela, COR_AMARELO_DIM, (meio-180, linha_y+5), (meio+180, linha_y+5), 1)

    # ── Cards de opção ───────────────────────────────────────────────────────

    def _desenhar_cards(self) -> None:
        card_w = 420
        card_h = 58
        gap    = 14
        total_h = len(OPCOES_MENU) * (card_h + gap) - gap
        inicio_y = (ALTURA_TELA - total_h) // 2 + 40

        for i, opcao in enumerate(OPCOES_MENU):
            selecionado = (i == self.indice_opcao_selecionada)
            cor_tema    = CORES_OPCAO[i]

            # Hover suave
            alvo = 8.0 if selecionado else 0.0
            self.offset_hover[i] += (alvo - self.offset_hover[i]) * 0.18
            ox = self.offset_hover[i]

            x = (LARGURA_TELA - card_w) // 2 + ox
            y = inicio_y + i * (card_h + gap)

            # Sombra
            s_sombra = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(s_sombra, (0,0,0,55), (4,4,card_w,card_h), border_radius=4)
            self.tela.blit(s_sombra, (x, y))

            # Corpo
            s_card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if selecionado:
                pygame.draw.rect(s_card, (*cor_tema, 45),  (0,0,card_w,card_h), border_radius=4)
                pygame.draw.rect(s_card, (*cor_tema, 255), (0,0,5,card_h),      border_radius=2)
                pygame.draw.rect(s_card, (*cor_tema, 190), (0,0,card_w,card_h), width=2, border_radius=4)
            else:
                pygame.draw.rect(s_card, (22,22,44,170), (0,0,card_w,card_h), border_radius=4)
                pygame.draw.rect(s_card, (60,60,90,100), (0,0,card_w,card_h), width=1, border_radius=4)
            self.tela.blit(s_card, (x, y))

            # Número retro
            num_surf = self.fonte_numero.render(f"{i+1:02d}", True,
                                                cor_tema if selecionado else (70,70,100))
            self.tela.blit(num_surf, (x+14, y + card_h//2 - num_surf.get_height()//2))

            # Separador vertical
            sep_x = x + 14 + num_surf.get_width() + 10
            pygame.draw.line(self.tela,
                             (*cor_tema, 160) if selecionado else (55,55,85),
                             (sep_x, y+12), (sep_x, y+card_h-12), 1)

            # Ícone
            ic_surf = self.fonte_icone.render(ICONES_MENU[i], True,
                                              cor_tema if selecionado else (90,90,120))
            ic_x = sep_x + 14
            self.tela.blit(ic_surf, (ic_x, y + card_h//2 - ic_surf.get_height()//2))

            # Texto
            cor_txt = COR_BRANCO if selecionado else COR_CINZA_CLARO
            txt_surf = self.fonte_opcao.render(opcao, True, cor_txt)
            self.tela.blit(txt_surf, (ic_x + ic_surf.get_width() + 16,
                                      y + card_h//2 - txt_surf.get_height()//2))

            # Seta piscante direita
            if selecionado and self.cursor_visivel:
                cx2 = x + card_w - 22
                cy2 = y + card_h // 2
                pygame.draw.polygon(self.tela, cor_tema,
                                    [(cx2,cy2-9),(cx2,cy2+9),(cx2+12,cy2)])

    # ── Rodapé ───────────────────────────────────────────────────────────────

    def _desenhar_rodape(self) -> None:
        partes = [
            ("↑↓", COR_AMARELO),
            (" navegar  ", (210, 210, 225)),
            ("ENTER", COR_AMARELO),
            (" confirmar  ", (210, 210, 225)),
            ("ESC", COR_AMARELO),
            (" sair", (210, 210, 225)),
        ]
        total_w = sum(self.fonte_ajuda.size(t)[0] for t, _ in partes)
        cx = (LARGURA_TELA - total_w) // 2
        cy = ALTURA_TELA - 36

        pygame.draw.line(self.tela, (40,40,65),
                         (LARGURA_TELA//2 - 280, cy-10),
                         (LARGURA_TELA//2 + 280, cy-10), 1)

        for texto, cor in partes:
            sombra = self.fonte_ajuda.render(texto, True, (0, 0, 0))
            surf = self.fonte_ajuda.render(texto, True, cor)
            self.tela.blit(sombra, (cx + 1, cy + 1))
            self.tela.blit(surf, (cx, cy))
            cx += surf.get_width()

    # ── Interface pública ────────────────────────────────────────────────────

    def processar_evento(self, evento: pygame.event.Event) -> Optional[str]:
        if evento.type != pygame.KEYDOWN:
            return None
        if evento.key == pygame.K_DOWN:
            self.indice_opcao_selecionada = (self.indice_opcao_selecionada + 1) % len(OPCOES_MENU)
            self.gerenciador_sons.tocar_efeito("navegacao_menu")
        elif evento.key == pygame.K_UP:
            self.indice_opcao_selecionada = (self.indice_opcao_selecionada - 1) % len(OPCOES_MENU)
            self.gerenciador_sons.tocar_efeito("navegacao_menu")
        elif evento.key == pygame.K_RETURN:
            self.gerenciador_sons.tocar_efeito("confirmacao_menu")
            return OPCOES_MENU[self.indice_opcao_selecionada]
        elif evento.key == pygame.K_ESCAPE:
            return "Sair"
        return None

    def atualizar(self, tempo_decorrido: float) -> None:
        self.tempo_total     += tempo_decorrido
        self.cronometro_piscar += tempo_decorrido
        if self.cronometro_piscar >= INTERVALO_PISCAR:
            self.cronometro_piscar = 0.0
            self.cursor_visivel = not self.cursor_visivel

    def desenhar(self) -> None:
        self._desenhar_fundo()
        self._desenhar_titulo()
        self._desenhar_cards()
        self._desenhar_rodape()