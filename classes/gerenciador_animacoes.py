import os
from typing import List, Tuple

import pygame

NOMES_QUADROS_IDLE: List[str] = ["idle_1.png", "idle_2.png", "idle_3.png"]
NOME_QUADRO_ATAQUE: str = "ataque.png"
NOME_QUADRO_DANO: str = "dano.png"

TAMANHO_PADRAO_PERSONAGEM: Tuple[int, int] = (220, 260)


class GerenciadorAnimacoes:
    """Carrega o conjunto completo de sprites de um personagem a partir de uma pasta."""

    def __init__(self, pasta_personagem: str, cor_placeholder: Tuple[int, int, int]) -> None:
        self.pasta_personagem = pasta_personagem
        self.cor_placeholder = cor_placeholder

        self.quadros_idle: List[pygame.Surface] = []
        self.quadro_ataque: pygame.Surface
        self.quadro_dano: pygame.Surface

        self._carregar_todos_os_quadros()

    def _carregar_imagem(self, nome_arquivo: str, rotulo_placeholder: str) -> pygame.Surface:
        """Tenta carregar uma imagem do disco; se não existir ou falhar, usa um placeholder."""
        caminho_completo = os.path.join(self.pasta_personagem, nome_arquivo)
        if os.path.isfile(caminho_completo):
            try:
                imagem_original = pygame.image.load(caminho_completo).convert_alpha()
                return pygame.transform.smoothscale(imagem_original, TAMANHO_PADRAO_PERSONAGEM)
            except pygame.error as erro:
                print(f"[AVISO] Falha ao carregar a imagem '{caminho_completo}': {erro}")
        return self._criar_placeholder(rotulo_placeholder)

    def _criar_placeholder(self, rotulo: str) -> pygame.Surface:
        """Gera uma superfície simples (retângulo colorido com rótulo) para um sprite ausente."""
        superficie = pygame.Surface(TAMANHO_PADRAO_PERSONAGEM, pygame.SRCALPHA)
        superficie.fill((0, 0, 0, 0))

        pygame.draw.rect(superficie, self.cor_placeholder, superficie.get_rect(), border_radius=18)
        pygame.draw.rect(superficie, (255, 255, 255), superficie.get_rect(), width=3, border_radius=18)

        try:
            fonte = pygame.font.SysFont("arial", 20, bold=True)
            texto_renderizado = fonte.render(rotulo, True, (255, 255, 255))
            posicao_texto = texto_renderizado.get_rect(center=superficie.get_rect().center)
            superficie.blit(texto_renderizado, posicao_texto)
        except pygame.error:
            pass  # Ambiente sem suporte a fontes: o placeholder colorido ainda funciona sem texto.

        return superficie

    def _carregar_todos_os_quadros(self) -> None:
        """Carrega os 3 quadros de idle, o quadro de ataque e o quadro de dano."""
        self.quadros_idle = [
            self._carregar_imagem(nome_arquivo, f"IDLE {indice + 1}")
            for indice, nome_arquivo in enumerate(NOMES_QUADROS_IDLE)
        ]
        self.quadro_ataque = self._carregar_imagem(NOME_QUADRO_ATAQUE, "ATAQUE")
        self.quadro_dano = self._carregar_imagem(NOME_QUADRO_DANO, "DANO")