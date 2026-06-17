import pygame

from classes.constantes import ALTURA_TELA, COR_BRANCO, COR_DESTAQUE, COR_FUNDO_PADRAO, LARGURA_TELA


class TelaInicial:
    """Exibe o título do jogo e aguarda o jogador pressionar uma tecla para avançar."""

    def __init__(self, tela: pygame.Surface) -> None:
        self.tela = tela
        self.fonte_titulo = pygame.font.SysFont("arial", 60, bold=True)
        self.fonte_instrucao = pygame.font.SysFont("arial", 26)
        self.cronometro_pulsar = 0.0

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        """Retorna True quando o jogador deseja avançar para a próxima tela."""
        return evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)

    def atualizar(self, tempo_decorrido: float) -> None:
        self.cronometro_pulsar += tempo_decorrido

    def desenhar(self) -> None:
        self.tela.fill(COR_FUNDO_PADRAO)

        texto_titulo = self.fonte_titulo.render("BATALHA DO CONHECIMENTO", True, COR_DESTAQUE)
        posicao_titulo = texto_titulo.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 40))
        self.tela.blit(texto_titulo, posicao_titulo)

        opacidade = int(155 + 100 * abs((self.cronometro_pulsar % 2.0) - 1.0))
        texto_instrucao = self.fonte_instrucao.render("Pressione qualquer tecla para começar", True, COR_BRANCO)
        texto_instrucao.set_alpha(opacidade)
        posicao_instrucao = texto_instrucao.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 60))
        self.tela.blit(texto_instrucao, posicao_instrucao)