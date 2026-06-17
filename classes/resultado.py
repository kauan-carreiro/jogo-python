import pygame

from classes.constantes import (
    ALTURA_TELA,
    COR_BRANCO,
    COR_DESTAQUE,
    COR_FUNDO_PADRAO,
    COR_VERDE,
    COR_VERMELHO,
    LARGURA_TELA,
)
from classes.jogador import Jogador


class Resultado:
    """Exibe as estatísticas finais e o vencedor da batalha."""

    def __init__(self, tela: pygame.Surface, dados: dict) -> None:
        self.tela = tela
        self.dados = dados
        self.vencedor: Jogador | None = dados.get("vencedor")
        self.jogador1: Jogador = dados["jogador1"]
        self.jogador2: Jogador = dados["jogador2"]
        self.tempo_total = dados.get("tempo_total_batalha", 0.0)

        self.fonte_titulo = pygame.font.SysFont("arial", 48, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("arial", 30, bold=True)
        self.fonte_texto = pygame.font.SysFont("arial", 24)
        self.fonte_instrucao = pygame.font.SysFont("arial", 20)

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        """Retorna True quando o jogador deseja voltar ao menu (ESC ou ENTER)."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return True
        return False

    def desenhar(self) -> None:
        self.tela.fill(COR_FUNDO_PADRAO)

        # Título
        if self.vencedor is None:
            titulo = "EMPATE!"
            cor_titulo = COR_DESTAQUE
        else:
            titulo = f"VENCEDOR: {self.vencedor.nome.upper()}"
            cor_titulo = COR_VERDE if self.vencedor is self.jogador1 else COR_VERMELHO

        texto_titulo = self.fonte_titulo.render(titulo, True, cor_titulo)
        self.tela.blit(texto_titulo, (LARGURA_TELA // 2 - texto_titulo.get_width() // 2, 40))

        # Tempo total
        texto_tempo = self.fonte_subtitulo.render(
            f"Tempo de batalha: {self.tempo_total:.1f}s", True, COR_BRANCO
        )
        self.tela.blit(texto_tempo, (LARGURA_TELA // 2 - texto_tempo.get_width() // 2, 100))

        # Estatísticas dos jogadores
        colunas = [
            ("Jogador", self.jogador1, 180),
            ("Jogador", self.jogador2, LARGURA_TELA - 180),
        ]

        for rotulo, jogador, pos_x in colunas:
            x = pos_x - 150  # centraliza o bloco
            y = 160

            # Nome
            nome_render = self.fonte_subtitulo.render(jogador.nome, True, COR_DESTAQUE)
            self.tela.blit(nome_render, (x + 150 - nome_render.get_width() // 2, y))
            y += 40

            # Vida
            vida_texto = f"Vida: {jogador.vida} / {jogador.vida_maxima}"
            vida_render = self.fonte_texto.render(vida_texto, True, COR_BRANCO)
            self.tela.blit(vida_render, (x, y))
            y += 30

            # Acertos e erros
            acertos = f"Acertos: {jogador.total_acertos}"
            erros = f"Erros: {jogador.total_erros}"
            self.tela.blit(self.fonte_texto.render(acertos, True, COR_VERDE), (x, y))
            self.tela.blit(self.fonte_texto.render(erros, True, COR_VERMELHO), (x + 200, y))
            y += 30

            # Dano total causado
            dano_texto = f"Dano causado: {jogador.dano_total_causado}"
            self.tela.blit(self.fonte_texto.render(dano_texto, True, COR_BRANCO), (x, y))
            y += 30

            # Tempo médio
            tempo_medio = jogador.calcular_tempo_medio()
            tempo_texto = f"Tempo médio: {tempo_medio:.2f}s" if tempo_medio else "Tempo médio: --"
            self.tela.blit(self.fonte_texto.render(tempo_texto, True, COR_BRANCO), (x, y))
            y += 30

            # Precisão
            precisao = jogador.calcular_precisao()
            precisao_texto = f"Precisão: {precisao:.1f}%"
            self.tela.blit(self.fonte_texto.render(precisao_texto, True, COR_BRANCO), (x, y))

        # Instrução para voltar
        instrucao = self.fonte_instrucao.render("Pressione ESC ou ENTER para voltar ao menu", True, COR_DESTAQUE)
        self.tela.blit(instrucao, (LARGURA_TELA // 2 - instrucao.get_width() // 2, ALTURA_TELA - 50))