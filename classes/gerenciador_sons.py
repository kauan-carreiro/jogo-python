import os
from typing import Dict, Optional

import pygame

from classes.constantes import PASTA_SONS

# ===================== VOLUMES (0.0 a 1.0) =====================
# Centralizado aqui para facilitar ajustes finos sem precisar caçar
# pygame.mixer.Sound.play() espalhado pelo código.

# Música e sons "ambiente"/decorativos: ficam baixos de propósito, para não
# disputar atenção nem incomodar o jogador.
VOLUME_SOM_DIGITACAO = 0.25
VOLUME_MUSICA_LOFI = 0.10
VOLUME_MUSICA_BATALHA = 0.10

# Efeitos sonoros de batalha: cada um pode ter seu próprio volume, já que os
# arquivos originais não necessariamente foram gravados no mesmo nível.
VOLUME_SOM_ATAQUE = 0.6
VOLUME_SOM_DANO = 0.6
VOLUME_SOM_VITORIA = 0.05
VOLUME_SOM_NAVEGACAO_MENU = 0.35
VOLUME_SOM_CONFIRMACAO_MENU = 0.5


class GerenciadorSons:
    """Gerencia efeitos sonoros e música de fundo de forma resiliente a falhas de áudio."""

    def __init__(self) -> None:
        self.audio_disponivel = True
        self.efeitos_sonoros: Dict[str, pygame.mixer.Sound] = {}
        self.caminho_musica_batalha = os.path.join(PASTA_SONS, "musica_batalha.mp3")
        self.caminho_musica_lofi = os.path.join(PASTA_SONS, "musica_lofi.mp3")

        # Canal dedicado ao som de digitação, para poder ligar/desligar o loop
        # sem afetar os demais efeitos sonoros.
        self.canal_digitacao: Optional[pygame.mixer.Channel] = None

        try:
            pygame.mixer.init()
        except pygame.error as erro:
            print(f"[AVISO] Sistema de áudio indisponível, o jogo continuará sem som: {erro}")
            self.audio_disponivel = False
            return

        self._carregar_efeito("ataque", "som_ataque.wav", VOLUME_SOM_ATAQUE)
        self._carregar_efeito("dano", "som_dano.wav", VOLUME_SOM_DANO)
        self._carregar_efeito("vitoria", "som_vitoria.wav", VOLUME_SOM_VITORIA)
        self._carregar_efeito("digitacao", "som_digitacao.mp3", VOLUME_SOM_DIGITACAO)
        self._carregar_efeito("navegacao_menu", "som_navegacao.mp3", VOLUME_SOM_NAVEGACAO_MENU)
        self._carregar_efeito("confirmacao_menu", "som_confirmacao.mp3", VOLUME_SOM_CONFIRMACAO_MENU)

    def _carregar_efeito(self, nome_chave: str, nome_arquivo: str, volume: float = 1.0) -> None:
        """Carrega um efeito sonoro do disco e já aplica o volume padrão dele,
        se o arquivo existir."""
        caminho_completo = os.path.join(PASTA_SONS, nome_arquivo)
        if os.path.isfile(caminho_completo):
            try:
                som = pygame.mixer.Sound(caminho_completo)
                som.set_volume(volume)
                self.efeitos_sonoros[nome_chave] = som
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
            pygame.mixer.music.set_volume(VOLUME_MUSICA_BATALHA)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as erro:
            print(f"[AVISO] Não foi possível tocar a música de batalha: {erro}")

    def tocar_musica_lofi(self) -> None:
        """Inicia a música lo-fi calma em loop (volume baixo), usada na tela inicial
        e na tela de história. Se o arquivo musica_lofi.mp3 não existir, não faz nada."""
        if not self.audio_disponivel or not os.path.isfile(self.caminho_musica_lofi):
            return
        try:
            pygame.mixer.music.load(self.caminho_musica_lofi)
            pygame.mixer.music.set_volume(VOLUME_MUSICA_LOFI)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as erro:
            print(f"[AVISO] Não foi possível tocar a música lo-fi: {erro}")

    def parar_musica(self) -> None:
        """Para a música de fundo, caso esteja tocando."""
        if self.audio_disponivel:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass

    def tocar_som_digitacao(self) -> None:
        """Inicia o som de digitação em loop (volume baixo), usado enquanto o texto
        da história vai sendo revelado letra por letra. Não faz nada se já estiver
        tocando, evitando reiniciar o som a cada chamada."""
        if not self.audio_disponivel:
            return
        som = self.efeitos_sonoros.get("digitacao")
        if som is None:
            return
        if self.canal_digitacao is not None and self.canal_digitacao.get_busy():
            return  # já está tocando, não reinicia
        som.set_volume(VOLUME_SOM_DIGITACAO)
        self.canal_digitacao = som.play(loops=-1)

    def parar_som_digitacao(self) -> None:
        """Para o som de digitação, caso esteja tocando (ex.: texto totalmente revelado)."""
        if self.canal_digitacao is not None:
            self.canal_digitacao.stop()
            self.canal_digitacao = None