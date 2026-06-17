import os
from typing import Dict

import pygame

from classes.constantes import PASTA_SONS


class GerenciadorSons:
    """Gerencia efeitos sonoros e música de fundo de forma resiliente a falhas de áudio."""

    def __init__(self) -> None:
        self.audio_disponivel = True
        self.efeitos_sonoros: Dict[str, pygame.mixer.Sound] = {}
        self.caminho_musica_batalha = os.path.join(PASTA_SONS, "musica_batalha.mp3")

        try:
            pygame.mixer.init()
        except pygame.error as erro:
            print(f"[AVISO] Sistema de áudio indisponível, o jogo continuará sem som: {erro}")
            self.audio_disponivel = False
            return

        self._carregar_efeito("ataque", "som_ataque.wav")
        self._carregar_efeito("dano", "som_dano.wav")
        self._carregar_efeito("vitoria", "som_vitoria.wav")

    def _carregar_efeito(self, nome_chave: str, nome_arquivo: str) -> None:
        """Carrega um efeito sonoro do disco, se o arquivo existir."""
        caminho_completo = os.path.join(PASTA_SONS, nome_arquivo)
        if os.path.isfile(caminho_completo):
            try:
                self.efeitos_sonoros[nome_chave] = pygame.mixer.Sound(caminho_completo)
            except pygame.error as erro:
                print(f"[AVISO] Não foi possível carregar o som '{nome_arquivo}': {erro}")

    def tocar_efeito(self, nome_chave: str) -> None:
        """Reproduz um efeito sonoro pelo nome (ataque, dano ou vitoria), se disponível."""
        if not self.audio_disponivel:
            return
        som = self.efeitos_sonoros.get(nome_chave)
        if som is not None:
            som.play()

    def tocar_musica_de_batalha(self) -> None:
        """Inicia a música de fundo da batalha em loop, se o arquivo musica_batalha.mp3 existir."""
        if not self.audio_disponivel or not os.path.isfile(self.caminho_musica_batalha):
            return
        try:
            pygame.mixer.music.load(self.caminho_musica_batalha)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as erro:
            print(f"[AVISO] Não foi possível tocar a música de batalha: {erro}")

    def parar_musica(self) -> None:
        """Para a música de fundo, caso esteja tocando."""
        if self.audio_disponivel:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass