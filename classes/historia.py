from typing import List

import pygame

from classes.constantes import ALTURA_TELA, COR_BRANCO, COR_DESTAQUE, COR_FUNDO_PADRAO, LARGURA_TELA

# Nova história, agora com um toque cômico e regional pernambucano.
# Dois estudantes competem para ver quem é o mais "sabido" nos descritores.
PARAGRAFOS_HISTORIA: List[str] = [
    "Era uma vez, em Recife, Pernambuco,",
    "dois jovens estudantes que se achavam os maiores conhecedores",
    "da Matemática e da Língua Portuguesa.",
    "",
    "Um se chamava Jeromel (o cabeludo, que vivia com a cabeça nas nuvens)",
    "e o outro, Felisberto (o rapaz dos olhos de jabuticaba, que não",
    "perdia uma aula).",
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


class Historia:
    VELOCIDADE_LETRA: float = 0.04   # segundos entre cada letra
    VELOCIDADE_RAPIDA: float = 0.01  # ao segurar ENTER/ESPAÇO

    def __init__(self, tela: pygame.Surface) -> None:
        self.tela = tela
        # Fontes mais modernas e com tamanho ajustado para o novo texto
        self.fonte_texto = pygame.font.SysFont("segoe ui", 26)
        self.fonte_instrucao = pygame.font.SysFont("segoe ui", 20, italic=True)

        self.indice_paragrafo_atual: int = 0
        self.letras_reveladas: int = 0
        self.paragrafos_completos: int = 0

        self.cronometro: float = 0.0
        self.tudo_revelado: bool = False

        self.cronometro_cursor: float = 0.0
        self.cursor_visivel: bool = True

    def reiniciar(self) -> None:
        self.indice_paragrafo_atual = 0
        self.letras_reveladas = 0
        self.paragrafos_completos = 0
        self.cronometro = 0.0
        self.tudo_revelado = False
        self.cronometro_cursor = 0.0
        self.cursor_visivel = True

    def _revelar_tudo(self) -> None:
        self.indice_paragrafo_atual = len(PARAGRAFOS_HISTORIA) - 1
        self.letras_reveladas = len(PARAGRAFOS_HISTORIA[-1])
        self.paragrafos_completos = len(PARAGRAFOS_HISTORIA) - 1
        self.tudo_revelado = True

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            tecla_avanco = (
                evento.type == pygame.MOUSEBUTTONDOWN
                or (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_RETURN))
            )
            if tecla_avanco:
                if self.tudo_revelado:
                    return True
                else:
                    self._revelar_tudo()
        return False

    def atualizar(self, tempo_decorrido: float) -> None:
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

    def desenhar(self) -> None:
        self.tela.fill(COR_FUNDO_PADRAO)

        # Gradiente de fundo sutil (opcional)
        for i in range(ALTURA_TELA):
            fator = i / ALTURA_TELA
            cor = (
                int(COR_FUNDO_PADRAO[0] * (1 - fator * 0.15)),
                int(COR_FUNDO_PADRAO[1] * (1 - fator * 0.15)),
                int(COR_FUNDO_PADRAO[2] * (1 - fator * 0.15)),
            )
            pygame.draw.line(self.tela, cor, (0, i), (LARGURA_TELA, i))

        posicao_y = 80

        # Parágrafos completos
        for i in range(self.paragrafos_completos):
            paragrafo = PARAGRAFOS_HISTORIA[i]
            if paragrafo:
                texto_renderizado = self.fonte_texto.render(paragrafo, True, COR_BRANCO)
                posicao_x = LARGURA_TELA // 2 - texto_renderizado.get_width() // 2
                self.tela.blit(texto_renderizado, (posicao_x, posicao_y))
            posicao_y += 34

        # Parágrafo atual sendo digitado
        if not self.tudo_revelado and self.indice_paragrafo_atual < len(PARAGRAFOS_HISTORIA):
            paragrafo_atual = PARAGRAFOS_HISTORIA[self.indice_paragrafo_atual]
            trecho_visivel = paragrafo_atual[: self.letras_reveladas]
            if trecho_visivel:
                texto_renderizado = self.fonte_texto.render(trecho_visivel, True, COR_BRANCO)
                posicao_x = LARGURA_TELA // 2 - texto_renderizado.get_width() // 2
                self.tela.blit(texto_renderizado, (posicao_x, posicao_y))

        # Mensagem inferior
        if self.tudo_revelado:
            msg = "Pressione ENTER para começar a batalha"
            if self.cursor_visivel:
                msg += " ▶"
        else:
            msg = "Pressione ENTER para pular toda a história"

        texto_instrucao = self.fonte_instrucao.render(msg, True, COR_DESTAQUE)
        self.tela.blit(
            texto_instrucao,
            (LARGURA_TELA // 2 - texto_instrucao.get_width() // 2, ALTURA_TELA - 60),
        )