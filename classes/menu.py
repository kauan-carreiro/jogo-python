from typing import List, Optional

import pygame

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


class Menu:
    """Controla a navegação e a seleção de opções do menu principal."""

    def __init__(self, tela: pygame.Surface) -> None:
        self.tela = tela
        self.fonte_titulo = pygame.font.SysFont("segoe ui", 60, bold=True)
        self.fonte_titulo_sec = pygame.font.SysFont("segoe ui", 52, bold=True)
        self.fonte_opcao = pygame.font.SysFont("segoe ui", 34)
        self.fonte_ajuda = pygame.font.SysFont("segoe ui", 20, italic=True)
        self.indice_opcao_selecionada = 0

        # Cores adicionais para efeitos
        self.cor_destaque_opcao = (255, 215, 0, 40)  # Amarelo com transparência
        self.cor_sombra = (0, 0, 0, 80)

    def processar_evento(self, evento: pygame.event.Event) -> Optional[str]:
        """
        Processa a entrada do teclado. Retorna a opção escolhida (texto) quando
        o jogador confirma uma seleção com ENTER, ou None caso contrário.
        """
        if evento.type != pygame.KEYDOWN:
            return None

        if evento.key == pygame.K_DOWN:
            self.indice_opcao_selecionada = (self.indice_opcao_selecionada + 1) % len(OPCOES_MENU)
        elif evento.key == pygame.K_UP:
            self.indice_opcao_selecionada = (self.indice_opcao_selecionada - 1) % len(OPCOES_MENU)
        elif evento.key == pygame.K_RETURN:
            return OPCOES_MENU[self.indice_opcao_selecionada]
        elif evento.key == pygame.K_ESCAPE:
            # Atalho ESC para sair (opcional)
            return "Sair"

        return None

    def _desenhar_titulo(self) -> None:
        """Renderiza o título 'MonitorAê - Game' com 'Aê' em branco e o restante amarelo."""
        # Divide o texto em partes
        parte1 = "Monitor"
        parte2 = "Aê"
        parte3 = " - Game"

        # Renderiza cada parte
        cor_amarela = COR_DESTAQUE
        cor_branca = COR_BRANCO

        texto1 = self.fonte_titulo.render(parte1, True, cor_amarela)
        texto2 = self.fonte_titulo_sec.render(parte2, True, cor_branca)  # um pouco menor para dar destaque
        texto3 = self.fonte_titulo.render(parte3, True, cor_amarela)

        # Calcula a largura total para centralizar
        largura_total = texto1.get_width() + texto2.get_width() + texto3.get_width()
        pos_x = (LARGURA_TELA - largura_total) // 2
        pos_y = 80

        # Sombra do título (opcional)
        sombra_offset = 3
        for parte, cor in [(texto1, cor_amarela), (texto2, cor_branca), (texto3, cor_amarela)]:
            sombra = parte.copy()
            sombra.fill((0, 0, 0, 80), None, pygame.BLEND_RGBA_MULT)  # escurece
            self.tela.blit(sombra, (pos_x + sombra_offset, pos_y + sombra_offset))
            self.tela.blit(parte, (pos_x, pos_y))
            pos_x += parte.get_width()

        # Linha decorativa abaixo do título
        linha_y = pos_y + texto1.get_height() + 15
        pygame.draw.line(self.tela, COR_CINZA_CLARO, (LARGURA_TELA // 2 - 200, linha_y),
                         (LARGURA_TELA // 2 + 200, linha_y), 2)

    def _desenhar_opcoes(self) -> None:
        """Desenha as opções com destaque para a selecionada."""
        posicao_y_inicial = 260
        espacamento = 70

        for indice, opcao in enumerate(OPCOES_MENU):
            esta_selecionada = indice == self.indice_opcao_selecionada
            y = posicao_y_inicial + indice * espacamento

            # Fundo para a opção selecionada (retângulo arredondado)
            if esta_selecionada:
                # Calcula o retângulo baseado no texto
                texto_temp = self.fonte_opcao.render(opcao, True, COR_BRANCO)
                largura_texto = texto_temp.get_width()
                altura_texto = texto_temp.get_height()
                rect_x = LARGURA_TELA // 2 - largura_texto // 2 - 30
                rect_y = y - 8
                rect_w = largura_texto + 60
                rect_h = altura_texto + 16

                # Desenha o fundo com borda arredondada e transparência
                s = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
                pygame.draw.rect(s, self.cor_destaque_opcao, (0, 0, rect_w, rect_h), border_radius=12)
                pygame.draw.rect(s, COR_DESTAQUE, (0, 0, rect_w, rect_h), width=2, border_radius=12)
                self.tela.blit(s, (rect_x, rect_y))

            # Texto da opção
            cor = COR_DESTAQUE if esta_selecionada else COR_BRANCO
            prefixo = "► " if esta_selecionada else "  "
            texto_renderizado = self.fonte_opcao.render(prefixo + opcao, True, cor)
            pos_x = LARGURA_TELA // 2 - texto_renderizado.get_width() // 2
            self.tela.blit(texto_renderizado, (pos_x, y))

    def desenhar(self) -> None:
        """Desenha todo o menu na tela."""
        self.tela.fill(COR_FUNDO_PADRAO)

        # Desenha um gradiente vertical suave no fundo (opcional)
        for i in range(ALTURA_TELA):
            fator = i / ALTURA_TELA
            cor = (
                int(COR_FUNDO_PADRAO[0] * (1 - fator * 0.3)),
                int(COR_FUNDO_PADRAO[1] * (1 - fator * 0.3)),
                int(COR_FUNDO_PADRAO[2] * (1 - fator * 0.3))
            )
            pygame.draw.line(self.tela, cor, (0, i), (LARGURA_TELA, i))

        self._desenhar_titulo()
        self._desenhar_opcoes()

        # Rodapé com instruções
        texto_ajuda = self.fonte_ajuda.render("↑ ↓ para navegar  •  ENTER para confirmar  •  ESC para sair", True, COR_CINZA_CLARO)
        self.tela.blit(texto_ajuda, (LARGURA_TELA // 2 - texto_ajuda.get_width() // 2, ALTURA_TELA - 50))
