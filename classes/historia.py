import math
from typing import List, Optional

import pygame

from classes.constantes import ALTURA_TELA, COR_BRANCO, COR_DESTAQUE, COR_FUNDO_PADRAO, LARGURA_TELA
from classes.gerenciador_sons import GerenciadorSons

PARAGRAFOS_HISTORIA: List[str] = [
    "Era uma vez, em Recife, Pernambuco, dois jovens estudantes que se achavam",
    "os maiores conhecedores da matemáticae da Língua Portuguesa.",
    "",
    "Um se chamava Jeromel (o cabeludo, que vivia com a cabeça nas nuvens)",
    "e o outro, Felisberto (o rapaz dos olhos de jabuticaba, que não perdia uma aula).",
    "",
    "Eles não se suportavam. Toda hora era um desafio:",
    "— Jeromel, quanto é 7 x 8? — 56, ué! — respondeu o Jeromel, todo orgulhoso.",
    "— Tá, mas qual o plural de 'capim'? — Felisberto disparou."
    "",
    "",
    "Jeromel e Felisberto aceitaram na hora. Pegaram suas canetas, seus cadernos",
    "e foram para a arena, que na verdade era o pátio da escola, com",
    "cadeiras enfileiradas e um quadro-negro gigante.",
    "",
    "",
    "Preparados? Então vamos nessa! Mostre que você sabe mais que Jeromel e Felisberto juntos!",
]

# Geometria da caixa — definida UMA vez, usada tanto no desenho quanto no texto
MARGEM_H    = 40
MARGEM_V    = 60
RODAPE_H    = 80   # altura reservada abaixo da caixa pro rodapé
BORDA_TOT   = 8    # 4px externa + 3px gap + 1px interna
PAD_INTERNO = 20   # respiro entre borda interna e conteúdo

COR_FUNDO       = (12, 12, 28)
COR_AMARELO     = (255, 210, 0)
COR_AMARELO_DIM = (100, 80, 0)
COR_TEXTO       = (220, 220, 240)
COR_CURSOR      = (255, 210, 0)
COR_PULAR       = (110, 110, 140)

GRID_SIZE = 32


class Historia:
    VELOCIDADE_LETRA: float = 0.04   # segundos entre cada letra
    VELOCIDADE_RAPIDA: float = 0.01  # ao segurar ENTER/ESPAÇO

    def __init__(self, tela: pygame.Surface, gerenciador_sons: Optional[GerenciadorSons] = None) -> None:
        self.tela = tela
        self.gerenciador_sons = gerenciador_sons
        self.fonte_texto = pygame.font.SysFont("segoe ui", 26)
        self.fonte_instrucao = pygame.font.SysFont("segoe ui", 20, italic=True)

        self.indice_paragrafo_atual: int = 0
        self.letras_reveladas: int = 0
        self.paragrafos_completos: int = 0
        self.cronometro: float = 0.0
        self.tudo_revelado: bool = False
        self.cronometro_cursor: float = 0.0
        self.cursor_visivel: bool = True
        self._tempo_total: float = 0.0
        self._pontos: list = self._gerar_pontos()

    def _gerar_pontos(self):
        import random
        pts = []
        for x in range(0, LARGURA_TELA + GRID_SIZE, GRID_SIZE):
            for y in range(0, ALTURA_TELA + GRID_SIZE, GRID_SIZE):
                pts.append((x, y, random.uniform(0, math.pi * 2)))
        return pts

    def reiniciar(self) -> None:
        self.indice_paragrafo_atual = 0
        self.letras_reveladas = 0
        self.paragrafos_completos = 0
        self.cronometro = 0.0
        self.tudo_revelado = False
        self.cronometro_cursor = 0.0
        self.cursor_visivel = True
        self._tempo_total = 0.0
        if self.gerenciador_sons:
            self.gerenciador_sons.tocar_som_digitacao()

    def _revelar_tudo(self) -> None:
        self.indice_paragrafo_atual = len(PARAGRAFOS_HISTORIA) - 1
        self.letras_reveladas = len(PARAGRAFOS_HISTORIA[-1])
        self.paragrafos_completos = len(PARAGRAFOS_HISTORIA) - 1
        self.tudo_revelado = True
        if self.gerenciador_sons:
            self.gerenciador_sons.parar_som_digitacao()

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            avanco = (
                evento.type == pygame.MOUSEBUTTONDOWN
                or (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_RETURN))
            )
            if avanco:
                if self.tudo_revelado:
                    return True
                else:
                    self._revelar_tudo()
        return False

    def atualizar(self, tempo_decorrido: float) -> None:
        self._tempo_total += tempo_decorrido
        if self.tudo_revelado:
            self.cronometro_cursor += tempo_decorrido
            if self.cronometro_cursor >= 0.5:
                self.cronometro_cursor = 0.0
                self.cursor_visivel = not self.cursor_visivel
            return

        teclas = pygame.key.get_pressed()
        velocidade = (
            self.VELOCIDADE_RAPIDA
            if (teclas[pygame.K_SPACE] or teclas[pygame.K_RETURN])
            else self.VELOCIDADE_LETRA
        )
        self.cronometro += tempo_decorrido
        while self.cronometro >= velocidade and not self.tudo_revelado:
            self.cronometro -= velocidade
            self._avancar_letra()

    def _avancar_letra(self) -> None:
        while self.indice_paragrafo_atual < len(PARAGRAFOS_HISTORIA):
            paragrafo = PARAGRAFOS_HISTORIA[self.indice_paragrafo_atual]
            if paragrafo == "":
                self.paragrafos_completos = self.indice_paragrafo_atual + 1
                self.indice_paragrafo_atual += 1
                self.letras_reveladas = 0
                continue
            if self.letras_reveladas < len(paragrafo):
                self.letras_reveladas += 1
                return
            else:
                self.paragrafos_completos = self.indice_paragrafo_atual + 1
                self.indice_paragrafo_atual += 1
                self.letras_reveladas = 0
            break
        if self.indice_paragrafo_atual >= len(PARAGRAFOS_HISTORIA):
            self.tudo_revelado = True
            self.cursor_visivel = True
            if self.gerenciador_sons:
                self.gerenciador_sons.parar_som_digitacao()

    # ------------------------------------------------------------------ #

    def desenhar(self) -> None:
        self.tela.fill(COR_FUNDO)
        self._desenhar_grade()
        self._desenhar_scanlines()
        self._desenhar_caixa_rpg()
        self._desenhar_texto_historia()
        self._desenhar_instrucao()

    def _desenhar_grade(self) -> None:
        for (x, y, fase) in self._pontos:
            alpha = int(18 + 14 * math.sin(self._tempo_total * 0.7 + fase))
            surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            surf.fill((70, 70, 150, alpha))
            self.tela.blit(surf, (x - 1, y - 1))

    def _desenhar_scanlines(self) -> None:
        for y in range(0, ALTURA_TELA, 4):
            surf = pygame.Surface((LARGURA_TELA, 1), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 25))
            self.tela.blit(surf, (0, y))

    def _desenhar_caixa_rpg(self) -> None:
        """Caixa de texto estilo RPG/pixel-art com borda dupla dourada."""
        x    = MARGEM_H
        y    = MARGEM_V
        larg = LARGURA_TELA - 2 * MARGEM_H
        alt  = ALTURA_TELA  - 2 * MARGEM_V - RODAPE_H

        pygame.draw.rect(self.tela, (16, 16, 36), (x, y, larg, alt))
        pygame.draw.rect(self.tela, COR_AMARELO,     (x,     y,     larg,     alt    ), 4)
        pygame.draw.rect(self.tela, COR_FUNDO,       (x + 4, y + 4, larg - 8, alt - 8), 3)
        pygame.draw.rect(self.tela, COR_AMARELO_DIM, (x + 7, y + 7, larg - 14, alt - 14), 1)

        tam = 10
        cantos = [
            (x, y), (x + larg - tam, y),
            (x, y + alt - tam), (x + larg - tam, y + alt - tam),
        ]
        for cx, cy in cantos:
            pygame.draw.rect(self.tela, COR_AMARELO, (cx, cy, tam, tam))
            pygame.draw.rect(self.tela, COR_FUNDO,   (cx + 2, cy + 2, tam - 4, tam - 4))

    def _desenhar_texto_historia(self) -> None:
        """Renderiza as linhas reveladas dentro da caixa RPG."""
        ESPACO_P = 30

        # Coordenadas derivadas diretamente da geometria da caixa
        pad_x = MARGEM_H + BORDA_TOT + PAD_INTERNO
        pad_y = MARGEM_V + BORDA_TOT + PAD_INTERNO

        linha_h = self.fonte_texto.get_linesize()

        # y_max: última posição Y onde uma linha ainda cabe inteira dentro da borda
        alt_caixa  = ALTURA_TELA - 2 * MARGEM_V - RODAPE_H
        y_fundo    = MARGEM_V + alt_caixa           # y da borda inferior externa
        y_max      = y_fundo - BORDA_TOT - PAD_INTERNO - linha_h

        # x_max: limite horizontal do texto (borda direita interna)
        larg_caixa = LARGURA_TELA - 2 * MARGEM_H
        x_max      = MARGEM_H + larg_caixa - BORDA_TOT - PAD_INTERNO

        y = pad_y
        for i, paragrafo in enumerate(PARAGRAFOS_HISTORIA):
            if y > y_max:
                break

            if paragrafo == "":
                y += ESPACO_P
                continue

            if i < self.paragrafos_completos:
                self._blit_linha(paragrafo, pad_x, y, COR_TEXTO, x_max)
            elif i == self.indice_paragrafo_atual and not self.tudo_revelado:
                trecho = paragrafo[: self.letras_reveladas]
                self._blit_linha(trecho, pad_x, y, COR_TEXTO, x_max)
                if self.cursor_visivel:
                    surf_c = self.fonte_texto.render("_", True, COR_CURSOR)
                    larg_trecho = self.fonte_texto.size(trecho)[0]
                    self.tela.blit(surf_c, (pad_x + larg_trecho + 2, y))

            y += linha_h

    def _blit_linha(self, texto: str, x: int, y: int, cor: tuple, x_max: int = 9999) -> None:
        surf = self.fonte_texto.render(texto, True, cor)
        self.tela.blit(surf, (x, y))

    def _desenhar_instrucao(self) -> None:
        if self.tudo_revelado:
            alpha = int(160 + 95 * math.sin(self._tempo_total * 4))
            msg = ">> Pressione ENTER para continuar <<"
            cor = COR_AMARELO
        else:
            alpha = 140
            msg = "[ ENTER = pular ]"
            cor = COR_PULAR

        surf = self.fonte_instrucao.render(msg, True, cor)
        surf.set_alpha(alpha)
        y = ALTURA_TELA - 38
        self.tela.blit(surf, (LARGURA_TELA // 2 - surf.get_width() // 2, y))