import os
import random
from typing import List, Tuple

import pygame

from classes.constantes import ALTURA_TELA, LARGURA_TELA

NOMES_CENARIOS: List[str] = [f"cenario_{numero}.png" for numero in range(1, 6)]

CORES_PLACEHOLDER_CENARIOS: List[Tuple[int, int, int]] = [
    (35, 40, 70),
    (60, 30, 50),
    (25, 55, 45),
    (55, 45, 20),
    (40, 25, 60),
]


class GerenciadorCenarios:
    """Gerencia o carregamento e o sorteio dos cenários de fundo da batalha."""

    def __init__(self, pasta_cenarios: str) -> None:
        self.pasta_cenarios = pasta_cenarios
        self.cenarios_carregados: List[pygame.Surface] = []
        self._carregar_cenarios()

    def _carregar_cenarios(self) -> None:
        """Carrega (ou cria placeholders para) os 5 cenários definidos em NOMES_CENARIOS."""
        for indice, nome_arquivo in enumerate(NOMES_CENARIOS):
            caminho_completo = os.path.join(self.pasta_cenarios, nome_arquivo)
            self.cenarios_carregados.append(self._carregar_imagem_de_cenario(caminho_completo, indice))

    def _carregar_imagem_de_cenario(self, caminho: str, indice: int) -> pygame.Surface:
        if os.path.isfile(caminho):
            try:
                imagem_original = pygame.image.load(caminho).convert()
                return pygame.transform.smoothscale(imagem_original, (LARGURA_TELA, ALTURA_TELA))
            except pygame.error as erro:
                print(f"[AVISO] Falha ao carregar o cenário '{caminho}': {erro}")
        return self._criar_cenario_placeholder(indice)

    def _criar_cenario_placeholder(self, indice: int) -> pygame.Surface:
        """Cria um fundo simples em degradê vertical quando a imagem do cenário não existe."""
        superficie = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        cor_base = CORES_PLACEHOLDER_CENARIOS[indice % len(CORES_PLACEHOLDER_CENARIOS)]

        for linha in range(ALTURA_TELA):
            fator_escurecimento = linha / ALTURA_TELA
            cor_da_linha = tuple(
                max(0, min(255, int(componente * (1 - fator_escurecimento * 0.5))))
                for componente in cor_base
            )
            pygame.draw.line(superficie, cor_da_linha, (0, linha), (LARGURA_TELA, linha))

        return superficie

    def sortear_cenario(self) -> pygame.Surface:
        """Sorteia aleatoriamente um cenário entre os disponíveis para a nova batalha."""
        return random.choice(self.cenarios_carregados)