from typing import Tuple

import pygame

from classes.constantes import DURACAO_ANIMACAO_ATAQUE, DURACAO_ANIMACAO_DANO, INTERVALO_TROCA_QUADRO_IDLE
from classes.gerenciador_animacoes import GerenciadorAnimacoes

ESTADO_OCIOSO = "ocioso"
ESTADO_ATACANDO = "atacando"
ESTADO_SOFRENDO_DANO = "sofrendo_dano"


class Personagem(pygame.sprite.Sprite):
    """Representa visualmente um jogador na arena de batalha."""

    def __init__(
        self,
        pasta_sprites: str,
        posicao: Tuple[float, float],
        cor_placeholder: Tuple[int, int, int],
        espelhado: bool = False,
    ) -> None:
        super().__init__()

        self.gerenciador_animacoes = GerenciadorAnimacoes(pasta_sprites, cor_placeholder)
        self.espelhado = espelhado

        self.estado_atual = ESTADO_OCIOSO
        self.indice_quadro_idle = 0
        self.cronometro_troca_quadro = 0.0
        self.cronometro_estado_temporario = 0.0

        # Atributos exigidos por pygame.sprite.Sprite: image e rect.
        self.image = self._obter_quadro_idle_atual()
        self.rect = self.image.get_rect(center=posicao)

    def _aplicar_espelhamento(self, superficie: pygame.Surface) -> pygame.Surface:
        """Espelha horizontalmente a imagem quando o personagem está do lado direito."""
        if self.espelhado:
            return pygame.transform.flip(superficie, True, False)
        return superficie

    def _obter_quadro_idle_atual(self) -> pygame.Surface:
        quadro = self.gerenciador_animacoes.quadros_idle[self.indice_quadro_idle]
        return self._aplicar_espelhamento(quadro)

    def iniciar_animacao_ataque(self) -> None:
        """Troca o personagem para o estado de ataque por um curto período."""
        self.estado_atual = ESTADO_ATACANDO
        self.cronometro_estado_temporario = 0.0

    def iniciar_animacao_dano(self) -> None:
        """Troca o personagem para o estado de sofrendo dano por um curto período."""
        self.estado_atual = ESTADO_SOFRENDO_DANO
        self.cronometro_estado_temporario = 0.0

    def update(self, tempo_decorrido: float) -> None:
        """
        Atualiza a animação do personagem a cada quadro do jogo.

        Sobrescreve o método 'update' de pygame.sprite.Sprite, permitindo que
        este personagem seja atualizado automaticamente por um pygame.sprite.Group.
        """
        if self.estado_atual == ESTADO_OCIOSO:
            self._atualizar_animacao_idle(tempo_decorrido)
            self.image = self._obter_quadro_idle_atual()

        elif self.estado_atual == ESTADO_ATACANDO:
            self.cronometro_estado_temporario += tempo_decorrido
            self.image = self._aplicar_espelhamento(self.gerenciador_animacoes.quadro_ataque)
            if self.cronometro_estado_temporario >= DURACAO_ANIMACAO_ATAQUE:
                self.estado_atual = ESTADO_OCIOSO

        elif self.estado_atual == ESTADO_SOFRENDO_DANO:
            self.cronometro_estado_temporario += tempo_decorrido
            self.image = self._aplicar_espelhamento(self.gerenciador_animacoes.quadro_dano)
            if self.cronometro_estado_temporario >= DURACAO_ANIMACAO_DANO:
                self.estado_atual = ESTADO_OCIOSO

    def _atualizar_animacao_idle(self, tempo_decorrido: float) -> None:
        """Os personagens nunca ficam totalmente estáticos: os quadros de idle alternam continuamente."""
        self.cronometro_troca_quadro += tempo_decorrido
        if self.cronometro_troca_quadro >= INTERVALO_TROCA_QUADRO_IDLE:
            self.cronometro_troca_quadro = 0.0
            quantidade_de_quadros = len(self.gerenciador_animacoes.quadros_idle)
            self.indice_quadro_idle = (self.indice_quadro_idle + 1) % quantidade_de_quadros