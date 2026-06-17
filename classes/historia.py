from typing import List

import pygame

from classes.constantes import ALTURA_TELA, COR_BRANCO, COR_DESTAQUE, COR_FUNDO_PADRAO, LARGURA_TELA

# A IA expandiu a ideia original de lore fornecida na especificação do projeto.
PARAGRAFOS_HISTORIA: List[str] = [
    "Há muito tempo, em uma escola perdida entre números e palavras,",
    "dois estudantes lendários treinaram por anos para dominar",
    "a Matemática e a Língua Portuguesa.",
    "",
    "Hoje, eles se encontram no Coliseu do Saber para o confronto final.",
    "Aqui, não vence quem possui mais força física.",
    "Vence quem pensa mais rápido e responde com precisão.",
    "",
    "Cada resposta correta se transforma em energia intelectual,",
    "um golpe invisível que atinge o adversário.",
    "",
    "O vencedor será coroado o novo Guardião do Conhecimento.",
    "",
    "Que comece a Batalha do Conhecimento!",
]


class Historia:
    """Exibe o texto da história de forma gradual, revelando um parágrafo por vez."""

    def __init__(self, tela: pygame.Surface) -> None:
        self.tela = tela
        self.fonte_texto = pygame.font.SysFont("arial", 28)
        self.fonte_instrucao = pygame.font.SysFont("arial", 20)
        self.indice_paragrafo_visivel = 0
        self.cronometro_revelacao = 0.0
        self.intervalo_revelacao = 0.7  # segundos entre cada novo parágrafo revelado

    def reiniciar(self) -> None:
        """Reinicia a revelação do texto, útil caso a história seja exibida novamente."""
        self.indice_paragrafo_visivel = 0
        self.cronometro_revelacao = 0.0

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        """Permite pular a história pressionando ESPAÇO/ENTER ou clicando com o mouse."""
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
            return True
        if evento.type == pygame.MOUSEBUTTONDOWN:
            return True
        return False

    def atualizar(self, tempo_decorrido: float) -> None:
        """Revela os parágrafos da história gradualmente, um a um."""
        self.cronometro_revelacao += tempo_decorrido
        if self.cronometro_revelacao >= self.intervalo_revelacao:
            self.cronometro_revelacao = 0.0
            if self.indice_paragrafo_visivel < len(PARAGRAFOS_HISTORIA):
                self.indice_paragrafo_visivel += 1

    def desenhar(self) -> None:
        self.tela.fill(COR_FUNDO_PADRAO)

        posicao_y = 100
        for paragrafo in PARAGRAFOS_HISTORIA[: self.indice_paragrafo_visivel]:
            if paragrafo:
                texto_renderizado = self.fonte_texto.render(paragrafo, True, COR_BRANCO)
                posicao_x = LARGURA_TELA // 2 - texto_renderizado.get_width() // 2
                self.tela.blit(texto_renderizado, (posicao_x, posicao_y))
            posicao_y += 38

        texto_instrucao = self.fonte_instrucao.render("Pressione ENTER para continuar", True, COR_DESTAQUE)
        self.tela.blit(texto_instrucao, (LARGURA_TELA // 2 - texto_instrucao.get_width() // 2, ALTURA_TELA - 60))