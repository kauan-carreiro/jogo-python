import math
import os
import random

import pygame

from classes.constantes import (
    ALTURA_TELA,
    COR_BRANCO,
    COR_DESTAQUE,
    COR_FUNDO_PADRAO,
    COR_VERDE,
    COR_VERMELHO,
    LARGURA_TELA,
    PASTA_PERSONAGENS,
    PASTA_CENARIOS,
)
from classes.jogador import Jogador

# ── Paleta idêntica às outras telas ─────────────────────────────────────────
COR_FUNDO        = (12, 12, 28)
COR_AMARELO      = (255, 210,  0)
COR_AMARELO_DIM  = (100,  80,  0)
COR_TEXTO        = (220, 220, 240)
GRID_SIZE        = 32

# Cores semânticas para o placar
COR_VITORIA  = ( 80, 220, 120)   # verde suave pixel-art
COR_DERROTA  = (220,  70,  70)   # vermelho suave
COR_EMPATE   = (255, 210,   0)   # dourado


class Resultado:
    """Tela de resultado com estética pixel-art/retro consistente com as demais telas."""

    SPRITE_LARGURA = 130
    SPRITE_ALTURA  = 160

    def __init__(self, tela: pygame.Surface, dados: dict) -> None:
        self.tela     = tela
        self.dados    = dados
        self.vencedor: Jogador | None = dados.get("vencedor")
        self.jogador1: Jogador        = dados["jogador1"]
        self.jogador2: Jogador        = dados["jogador2"]
        self.tempo_total              = dados.get("tempo_total_batalha", 0.0)

        # Fontes: mono/pixel igual às outras telas
        self.fonte_titulo    = pygame.font.SysFont("couriernew,courier,monospace", 44, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("couriernew,courier,monospace", 20, bold=True)
        self.fonte_label     = pygame.font.SysFont("couriernew,courier,monospace", 11, bold=True)
        self.fonte_valor     = pygame.font.SysFont("couriernew,courier,monospace", 16)
        self.fonte_ajuda     = pygame.font.SysFont("couriernew,courier,monospace", 13)
        self.fonte_nome      = pygame.font.SysFont("couriernew,courier,monospace", 20, bold=True)
        self.fonte_badge     = pygame.font.SysFont("couriernew,courier,monospace", 12, bold=True)

        # Pré-gera grade de pontos (igual tela_inicial / menu / historia)
        self._pontos_grade = [
            (x, y, random.uniform(0, math.pi * 2))
            for x in range(0, LARGURA_TELA + GRID_SIZE, GRID_SIZE)
            for y in range(0, ALTURA_TELA  + GRID_SIZE, GRID_SIZE)
        ]
        self._tempo_total_anim = 0.0

        # Sprites
        self.sprite1 = self._carregar_sprite("player1", self._jogador_venceu(self.jogador1))
        self.sprite2 = self._carregar_sprite("player2", self._jogador_venceu(self.jogador2))

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _jogador_venceu(self, jogador: Jogador) -> bool:
        return self.vencedor is not None and self.vencedor is jogador

    def _carregar_sprite(self, pasta: str, venceu: bool) -> pygame.Surface:
        nome_arquivo = "idle_vitoria.png" if venceu else "idle_derrota.png"
        caminho = os.path.join(PASTA_PERSONAGENS, pasta, nome_arquivo)
        if os.path.isfile(caminho):
            try:
                img = pygame.image.load(caminho).convert_alpha()
                return pygame.transform.smoothscale(img, (self.SPRITE_LARGURA, self.SPRITE_ALTURA))
            except pygame.error:
                pass
        # Placeholder pixel-art (retângulo com borda e ícone)
        cor_borda = COR_VITORIA if venceu else COR_DERROTA
        surf = pygame.Surface((self.SPRITE_LARGURA, self.SPRITE_ALTURA), pygame.SRCALPHA)
        surf.fill((18, 18, 38))
        pygame.draw.rect(surf, cor_borda, surf.get_rect(), 3)
        fonte_ph = pygame.font.SysFont("couriernew,courier,monospace", 36, bold=True)
        icone = fonte_ph.render("★" if venceu else "✕", True, cor_borda)
        surf.blit(icone, (self.SPRITE_LARGURA//2 - icone.get_width()//2,
                          self.SPRITE_ALTURA//2  - icone.get_height()//2))
        return surf

    # ── Fundo (idêntico às outras telas) ─────────────────────────────────────

    def _desenhar_fundo(self) -> None:
        self.tela.fill(COR_FUNDO)
        for (x, y, fase) in self._pontos_grade:
            alpha = int(25 + 20 * math.sin(self._tempo_total_anim * 0.8 + fase))
            surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            surf.fill((80, 80, 160, alpha))
            self.tela.blit(surf, (x - 1, y - 1))
        for y in range(0, ALTURA_TELA, 4):
            surf = pygame.Surface((LARGURA_TELA, 1), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 30))
            self.tela.blit(surf, (0, y))

    # ── Caixa pixel-art (mesma lógica de historia.py) ────────────────────────

    def _desenhar_caixa(self, x: int, y: int, larg: int, alt: int,
                        cor_borda=None) -> None:
        cor = cor_borda or COR_AMARELO
        dim = tuple(max(0, c - 120) for c in cor)

        pygame.draw.rect(self.tela, (16, 16, 36), (x, y, larg, alt))
        pygame.draw.rect(self.tela, cor,       (x,     y,     larg,      alt     ), 4)
        pygame.draw.rect(self.tela, COR_FUNDO, (x + 4, y + 4, larg - 8,  alt - 8 ), 3)
        pygame.draw.rect(self.tela, dim,       (x + 7, y + 7, larg - 14, alt - 14), 1)

        tam = 8
        for cx, cy in [(x, y), (x+larg-tam, y), (x, y+alt-tam), (x+larg-tam, y+alt-tam)]:
            pygame.draw.rect(self.tela, cor,       (cx,   cy,   tam,   tam  ))
            pygame.draw.rect(self.tela, COR_FUNDO, (cx+2, cy+2, tam-4, tam-4))

    # ── Título principal ──────────────────────────────────────────────────────

    def _desenhar_titulo(self) -> None:
        if self.vencedor is None:
            texto   = "== EMPATE! =="
            cor_txt = COR_EMPATE
        else:
            texto   = f"VENCEDOR: {self.vencedor.nome.upper()}"
            cor_txt = COR_VITORIA if self.vencedor is self.jogador1 else COR_DERROTA

        sombra = self.fonte_titulo.render(texto, True, (0, 0, 0))
        titulo = self.fonte_titulo.render(texto, True, cor_txt)
        cx = LARGURA_TELA // 2
        ty = 24
        self.tela.blit(sombra, (cx - titulo.get_width()//2 + 3, ty + 3))
        self.tela.blit(titulo, (cx - titulo.get_width()//2,     ty))

        # Linha dupla decorativa (igual ao menu)
        ly = ty + titulo.get_height() + 8
        pygame.draw.line(self.tela, COR_AMARELO,    (cx-280, ly),   (cx+280, ly),   2)
        pygame.draw.line(self.tela, COR_AMARELO_DIM,(cx-200, ly+5), (cx+200, ly+5), 1)

        # Tempo de batalha
        tempo_str  = f"[ tempo de batalha: {self.tempo_total:.1f}s ]"
        tempo_surf = self.fonte_subtitulo.render(tempo_str, True, (210, 210, 230))
        self.tela.blit(tempo_surf, (cx - tempo_surf.get_width()//2, ly + 12))

    # ── Painel de um jogador ──────────────────────────────────────────────────

    def _desenhar_painel_jogador(self, jogador: Jogador, x: int, y: int,
                                  venceu: bool, sprite: pygame.Surface) -> None:
        larg, alt = 270, 330
        cor_borda = COR_VITORIA if venceu else COR_DERROTA

        self._desenhar_caixa(x, y, larg, alt, cor_borda)

        pad = 12

        # Badge VITÓRIA / DERROTA sobrepondo a borda superior
        badge_txt  = " VITÓRIA " if venceu else " DERROTA "
        badge_surf = self.fonte_badge.render(badge_txt, True, COR_FUNDO)
        badge_bg   = pygame.Surface((badge_surf.get_width() + 6, badge_surf.get_height() + 4), pygame.SRCALPHA)
        badge_bg.fill((*cor_borda, 255))
        bx = x + larg//2 - badge_bg.get_width()//2
        by = y - badge_bg.get_height()//2
        self.tela.blit(badge_bg,   (bx, by))
        self.tela.blit(badge_surf, (bx + 3, by + 2))

        # Nome do jogador
        nome_surf = self.fonte_nome.render(jogador.nome, True, COR_AMARELO)
        self.tela.blit(nome_surf, (x + larg//2 - nome_surf.get_width()//2, y + pad + 4))

        # Separador fino
        sep_y = y + pad + 4 + nome_surf.get_height() + 6
        pygame.draw.line(self.tela, COR_AMARELO_DIM, (x + pad, sep_y), (x + larg - pad, sep_y), 1)

        # Sprite centralizado
        sprite_x = x + larg//2 - sprite.get_width()//2
        sprite_y = sep_y + 8
        self.tela.blit(sprite, (sprite_x, sprite_y))

        # Stats em grade 2 colunas
        stats = [
            ("VIDA",     f"{jogador.vida}/{jogador.vida_maxima}"),
            ("ACERTOS",  str(jogador.total_acertos)),
            ("ERROS",    str(jogador.total_erros)),
            ("DANO",     str(jogador.dano_total_causado)),
            ("T.MÉDIO",  f"{jogador.calcular_tempo_medio():.2f}s" if jogador.calcular_tempo_medio() else "--"),
            ("PRECISÃO", f"{jogador.calcular_precisao():.0f}%"),
        ]

        stat_y = sprite_y + sprite.get_height() + 10
        col_w  = (larg - 2 * pad) // 2
        row_h  = 32

        for idx, (label, valor) in enumerate(stats):
            col_x = x + pad + (idx % 2) * col_w
            row_y = stat_y + (idx // 2) * row_h
            lbl_s = self.fonte_label.render(label, True, (190, 190, 215))
            val_s = self.fonte_valor.render(valor, True, COR_TEXTO)
            self.tela.blit(lbl_s, (col_x, row_y))
            self.tela.blit(val_s, (col_x, row_y + lbl_s.get_height() + 1))

    # ── VS central pulsante ───────────────────────────────────────────────────

    def _desenhar_vs(self, cy: int) -> None:
        cx   = LARGURA_TELA // 2
        surf = self.fonte_titulo.render("VS", True, COR_AMARELO)
        alpha = int(160 + 95 * math.sin(self._tempo_total_anim * 2.5))
        surf.set_alpha(alpha)
        self.tela.blit(surf, (cx - surf.get_width()//2, cy - surf.get_height()//2))

    # ── Rodapé (igual ao menu) ────────────────────────────────────────────────

    def _desenhar_rodape(self) -> None:
        partes = [
            ("ENTER", COR_AMARELO),
            (" / ",   (60, 60, 90)),
            ("ESC",   COR_AMARELO),
            ("  voltar ao menu", (210, 210, 225)),
        ]
        total_w = sum(self.fonte_ajuda.size(t)[0] for t, _ in partes)
        cx = (LARGURA_TELA - total_w) // 2
        cy = ALTURA_TELA - 32

        pygame.draw.line(self.tela, (40, 40, 65),
                         (LARGURA_TELA//2 - 280, cy - 10),
                         (LARGURA_TELA//2 + 280, cy - 10), 1)

        for texto, cor in partes:
            sombra = self.fonte_ajuda.render(texto, True, (0, 0, 0))
            surf = self.fonte_ajuda.render(texto, True, cor)
            self.tela.blit(sombra, (cx + 1, cy + 1))
            self.tela.blit(surf, (cx, cy))
            cx += surf.get_width()

    # ── Interface pública ─────────────────────────────────────────────────────

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type == pygame.KEYDOWN:
            return evento.key in (pygame.K_ESCAPE, pygame.K_RETURN)
        return False

    def atualizar(self, tempo_decorrido: float) -> None:
        self._tempo_total_anim += tempo_decorrido

    def desenhar(self) -> None:
        self._desenhar_fundo()
        self._desenhar_titulo()

        painel_larg = 270
        painel_alt  = 330
        gap_centro  = 100
        total_w     = painel_larg * 2 + gap_centro
        inicio_x    = (LARGURA_TELA - total_w) // 2
        painel_y    = 128

        x1 = inicio_x
        x2 = inicio_x + painel_larg + gap_centro

        self._desenhar_painel_jogador(self.jogador1, x1, painel_y,
                                       self._jogador_venceu(self.jogador1), self.sprite1)
        self._desenhar_painel_jogador(self.jogador2, x2, painel_y,
                                       self._jogador_venceu(self.jogador2), self.sprite2)

        self._desenhar_vs(painel_y + painel_alt // 2)
        self._desenhar_rodape()