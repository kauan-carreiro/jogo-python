import os
import random
from typing import List, Optional

import pygame

from classes.calculadora_dano import CalculadoraDano
from classes.constantes import (
    ALTURA_TELA,
    COR_AMARELO,
    COR_BRANCO,
    COR_CINZA,
    COR_CINZA_CLARO,
    COR_DESTAQUE,
    COR_VERDE,
    COR_VERMELHO,
    LARGURA_TELA,
    PASTA_PERSONAGENS,
    QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA,
    TECLAS_JOGADOR_1,
    TECLAS_JOGADOR_2,
    TEMPO_EXIBICAO_RESULTADO_RODADA,
    TEMPO_LEITURA_PERGUNTA,
    TEMPO_LIMITE_RESPOSTA,
    VIDA_INICIAL,
)
from classes.gerenciador_cenarios import GerenciadorCenarios
from classes.gerenciador_perguntas import GerenciadorPerguntas
from classes.gerenciador_sons import GerenciadorSons
from classes.jogador import Jogador
from classes.personagem import Personagem

ESTADO_RODADA_AGUARDANDO_RESPOSTAS = "aguardando_respostas"
ESTADO_RODADA_EXIBINDO_RESULTADO = "exibindo_resultado"
ESTADO_RODADA_FIM_DE_BATALHA = "fim_de_batalha"

# Pesos de sorteio de dificuldade
PESOS_DIFICULDADE = {"facil": 0.40, "normal": 0.35, "dificil": 0.25}

class Batalha:
    def __init__(
        self,
        tela: pygame.Surface,
        modo_jogo: str,
        gerenciador_perguntas: GerenciadorPerguntas,
        gerenciador_cenarios: GerenciadorCenarios,
        gerenciador_sons: GerenciadorSons,
    ) -> None:
        self.tela = tela
        self.modo_jogo = modo_jogo
        self.gerenciador_perguntas = gerenciador_perguntas
        self.gerenciador_cenarios = gerenciador_cenarios
        self.gerenciador_sons = gerenciador_sons

        # Cada nova batalha sorteia um cenário e zera o controle de perguntas repetidas.
        self.gerenciador_perguntas.reiniciar_controle_de_repeticao()
        self.cenario_atual = self.gerenciador_cenarios.sortear_cenario()

        self.jogador1 = Jogador("Player 1", TECLAS_JOGADOR_1, VIDA_INICIAL)
        self.jogador2 = Jogador("Player 2", TECLAS_JOGADOR_2, VIDA_INICIAL)

        self.personagem1 = Personagem(
            os.path.join(PASTA_PERSONAGENS, "player1"),
            (LARGURA_TELA * 0.27, ALTURA_TELA * 0.62),
            (40, 90, 200),
            espelhado=False,
        )
        self.personagem2 = Personagem(
            os.path.join(PASTA_PERSONAGENS, "player2"),
            (LARGURA_TELA * 0.73, ALTURA_TELA * 0.62),
            (200, 60, 60),
            espelhado=True,
        )
        self.grupo_personagens = pygame.sprite.Group(self.personagem1, self.personagem2)

        self.pergunta_atual = None
        self.estado_rodada = ESTADO_RODADA_AGUARDANDO_RESPOSTAS
        self.respostas_habilitadas = False
        self.cronometro_rodada = 0.0
        self.cronometro_resposta = 0.0
        self.cronometro_resultado = 0.0
        self.alguem_acertou_primeiro_na_rodada = False
        self.contador_perguntas_respondidas = 0
        self.tempo_total_batalha = 0.0
        self.vencedor: Optional[Jogador] = None
        self.batalha_finalizada = False

        self.fonte_pergunta = pygame.font.SysFont("arial", 25, bold=True)
        self.fonte_alternativa = pygame.font.SysFont("arial", 21)
        self.fonte_hud = pygame.font.SysFont("arial", 20, bold=True)
        self.fonte_pequena = pygame.font.SysFont("arial", 16)

        self.gerenciador_sons.tocar_musica_de_batalha()
        self._iniciar_nova_rodada()

    # ----------------------------------------------------------------- #
    # CICLO DE RODADAS
    # ----------------------------------------------------------------- #
    def _escolher_dificuldade_aleatoria(self) -> str:
        """Sorteia a dificuldade da próxima pergunta com base nos pesos de balanceamento."""
        dificuldades = list(PESOS_DIFICULDADE.keys())
        pesos = list(PESOS_DIFICULDADE.values())
        return random.choices(dificuldades, weights=pesos, k=1)[0]

    def _iniciar_nova_rodada(self) -> None:
        """Sorteia uma nova pergunta e reinicia todo o estado referente à rodada."""
        dificuldade_sorteada = self._escolher_dificuldade_aleatoria()
        pergunta_sorteada = self.gerenciador_perguntas.sortear_pergunta_para_modo(
            self.modo_jogo, dificuldade_sorteada
        )

        # Se não houver perguntas disponíveis na dificuldade sorteada (por exemplo,
        # porque o banco de questões já foi todo utilizado), tenta as demais antes de desistir.
        if pergunta_sorteada is None:
            for dificuldade_alternativa in ("normal", "facil", "dificil"):
                pergunta_sorteada = self.gerenciador_perguntas.sortear_pergunta_para_modo(
                    self.modo_jogo, dificuldade_alternativa
                )
                if pergunta_sorteada is not None:
                    break

        if pergunta_sorteada is None:
            self._finalizar_batalha()
            return

        self.pergunta_atual = pergunta_sorteada
        self.jogador1.reiniciar_para_nova_rodada()
        self.jogador2.reiniciar_para_nova_rodada()
        self.estado_rodada = ESTADO_RODADA_AGUARDANDO_RESPOSTAS
        self.respostas_habilitadas = False
        self.cronometro_rodada = 0.0
        self.cronometro_resposta = 0.0
        self.alguem_acertou_primeiro_na_rodada = False

    def _processar_resposta_jogador(
        self,
        jogador: Jogador,
        oponente: Jogador,
        personagem_jogador: Personagem,
        personagem_oponente: Personagem,
        letra: str,
    ) -> None:
        """Processa a escolha de alternativa de um jogador: calcula dano e atualiza estatísticas."""
        if jogador.ja_respondeu_na_rodada or not self.respostas_habilitadas:
            return

        tempo_resposta = self.cronometro_resposta
        jogador.registrar_resposta(letra, tempo_resposta)

        resposta_correta = self.pergunta_atual.verificar_resposta(letra)
        foi_o_primeiro_a_acertar = resposta_correta and not self.alguem_acertou_primeiro_na_rodada
        if resposta_correta:
            self.alguem_acertou_primeiro_na_rodada = True

        dano_causado = CalculadoraDano.calcular_dano(
            resposta_correta, self.pergunta_atual.dificuldade, tempo_resposta, foi_o_primeiro_a_acertar
        )

        if resposta_correta:
            jogador.registrar_acerto(dano_causado)
            oponente.receber_dano(dano_causado)
            personagem_jogador.iniciar_animacao_ataque()
            personagem_oponente.iniciar_animacao_dano()
            self.gerenciador_sons.tocar_efeito("ataque")
            self.gerenciador_sons.tocar_efeito("dano")
        else:
            jogador.registrar_erro()

    def processar_evento(self, evento: pygame.event.Event) -> None:
        """Processa eventos de teclado para a seleção de alternativas pelos dois jogadores."""
        if evento.type != pygame.KEYDOWN or self.estado_rodada != ESTADO_RODADA_AGUARDANDO_RESPOSTAS:
            return

        letra_jogador1 = self.jogador1.obter_letra_pela_tecla(evento.key)
        if letra_jogador1:
            self._processar_resposta_jogador(
                self.jogador1, self.jogador2, self.personagem1, self.personagem2, letra_jogador1
            )

        letra_jogador2 = self.jogador2.obter_letra_pela_tecla(evento.key)
        if letra_jogador2:
            self._processar_resposta_jogador(
                self.jogador2, self.jogador1, self.personagem2, self.personagem1, letra_jogador2
            )

    def _verificar_fim_da_rodada(self) -> None:
        """Verifica se a rodada deve terminar: ambos responderam ou o tempo se esgotou."""
        ambos_responderam = self.jogador1.ja_respondeu_na_rodada and self.jogador2.ja_respondeu_na_rodada
        tempo_esgotado = self.cronometro_resposta >= TEMPO_LIMITE_RESPOSTA

        if not (ambos_responderam or tempo_esgotado):
            return

        if tempo_esgotado:
            # Quem não respondeu a tempo perde a rodada (contabilizado como erro).
            for jogador in (self.jogador1, self.jogador2):
                if not jogador.ja_respondeu_na_rodada:
                    jogador.ja_respondeu_na_rodada = True
                    jogador.registrar_erro()

        self.contador_perguntas_respondidas += 1
        self.estado_rodada = ESTADO_RODADA_EXIBINDO_RESULTADO
        self.cronometro_resultado = 0.0

    def _determinar_vencedor(self) -> Optional[Jogador]:
        """Define o vencedor da batalha com base na vida restante e critérios de desempate."""
        if self.jogador1.vida <= 0 and self.jogador2.vida > 0:
            return self.jogador2
        if self.jogador2.vida <= 0 and self.jogador1.vida > 0:
            return self.jogador1
        if self.jogador1.vida != self.jogador2.vida:
            return self.jogador1 if self.jogador1.vida > self.jogador2.vida else self.jogador2

        # Empate de vida: desempata por número de acertos e, em seguida, por tempo médio.
        if self.jogador1.total_acertos != self.jogador2.total_acertos:
            return self.jogador1 if self.jogador1.total_acertos > self.jogador2.total_acertos else self.jogador2

        tempo_medio_jogador1 = self.jogador1.calcular_tempo_medio() or float("inf")
        tempo_medio_jogador2 = self.jogador2.calcular_tempo_medio() or float("inf")
        if tempo_medio_jogador1 == tempo_medio_jogador2:
            return None  # Empate verdadeiro, sem critério de desempate restante.
        return self.jogador1 if tempo_medio_jogador1 < tempo_medio_jogador2 else self.jogador2

    def _finalizar_batalha(self) -> None:
        """Encerra a batalha, define o vencedor e para a música de fundo."""
        self.estado_rodada = ESTADO_RODADA_FIM_DE_BATALHA
        self.batalha_finalizada = True
        self.vencedor = self._determinar_vencedor()

        self.gerenciador_sons.parar_musica()
        self.gerenciador_sons.tocar_efeito("vitoria")

    def obter_dados_resultado(self) -> dict:
        """Consolida as estatísticas finais da batalha para serem exibidas na tela de resultado."""
        return {
            "modo_jogo": self.modo_jogo,
            "tempo_total_batalha": self.tempo_total_batalha,
            "vencedor": self.vencedor,
            "jogador1": self.jogador1,
            "jogador2": self.jogador2,
        }

    # ----------------------------------------------------------------- #
    # ATUALIZAÇÃO
    # ----------------------------------------------------------------- #
    def atualizar(self, tempo_decorrido: float) -> None:
        """Atualiza o estado da rodada, as animações dos personagens e os cronômetros."""
        if self.batalha_finalizada:
            return

        self.tempo_total_batalha += tempo_decorrido
        self.grupo_personagens.update(tempo_decorrido)

        if self.estado_rodada == ESTADO_RODADA_AGUARDANDO_RESPOSTAS:
            self.cronometro_rodada += tempo_decorrido

            if not self.respostas_habilitadas and self.cronometro_rodada >= TEMPO_LEITURA_PERGUNTA:
                self.respostas_habilitadas = True

            if self.respostas_habilitadas:
                self.cronometro_resposta += tempo_decorrido
                self._verificar_fim_da_rodada()

        elif self.estado_rodada == ESTADO_RODADA_EXIBINDO_RESULTADO:
            self.cronometro_resultado += tempo_decorrido
            if self.cronometro_resultado >= TEMPO_EXIBICAO_RESULTADO_RODADA:
                houve_derrota = self.jogador1.esta_derrotado() or self.jogador2.esta_derrotado()
                atingiu_limite_de_perguntas = (
                    self.contador_perguntas_respondidas >= QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA
                )
                if houve_derrota or atingiu_limite_de_perguntas:
                    self._finalizar_batalha()
                else:
                    self._iniciar_nova_rodada()

    # ----------------------------------------------------------------- #
    # DESENHO / INTERFACE
    # ----------------------------------------------------------------- #
    def _quebrar_texto(self, texto: str, fonte: pygame.font.Font, largura_maxima: int) -> List[str]:
        """Quebra um texto longo em múltiplas linhas que cabem na largura disponível."""
        palavras = texto.split(" ")
        linhas: List[str] = []
        linha_atual = ""

        for palavra in palavras:
            linha_de_teste = f"{linha_atual} {palavra}".strip()
            if fonte.size(linha_de_teste)[0] <= largura_maxima:
                linha_atual = linha_de_teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra

        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def _desenhar_barra_de_vida(self, jogador: Jogador, posicao_x: int, posicao_y: int) -> None:
        largura_barra = 320
        altura_barra = 26
        proporcao_vida = max(0.0, jogador.vida / jogador.vida_maxima)

        pygame.draw.rect(self.tela, COR_CINZA, (posicao_x, posicao_y, largura_barra, altura_barra), border_radius=6)

        if proporcao_vida > 0.4:
            cor_vida = COR_VERDE
        elif proporcao_vida > 0.15:
            cor_vida = COR_AMARELO
        else:
            cor_vida = COR_VERMELHO

        pygame.draw.rect(
            self.tela,
            cor_vida,
            (posicao_x, posicao_y, int(largura_barra * proporcao_vida), altura_barra),
            border_radius=6,
        )
        pygame.draw.rect(self.tela, COR_BRANCO, (posicao_x, posicao_y, largura_barra, altura_barra), width=2, border_radius=6)

        texto_vida = self.fonte_hud.render(f"{jogador.vida}/{jogador.vida_maxima}", True, COR_BRANCO)
        self.tela.blit(texto_vida, (posicao_x + largura_barra // 2 - texto_vida.get_width() // 2, posicao_y + 2))

    def _desenhar_painel_jogador(self, jogador: Jogador, posicao_x: int, posicao_y: int, alinhado_a_direita: bool) -> None:
        nome_renderizado = self.fonte_hud.render(jogador.nome, True, COR_DESTAQUE)
        texto_x = posicao_x if not alinhado_a_direita else posicao_x - nome_renderizado.get_width()
        self.tela.blit(nome_renderizado, (texto_x, posicao_y - 26))

        posicao_x_barra = posicao_x if not alinhado_a_direita else posicao_x - 320
        self._desenhar_barra_de_vida(jogador, posicao_x_barra, posicao_y)

        texto_informativo = (
            f"Acertos: {jogador.total_acertos}  Erros: {jogador.total_erros}  "
            f"Último dano: {jogador.ultimo_dano_causado}"
        )
        texto_renderizado = self.fonte_pequena.render(texto_informativo, True, COR_CINZA_CLARO)
        info_x = posicao_x if not alinhado_a_direita else posicao_x - texto_renderizado.get_width()
        self.tela.blit(texto_renderizado, (info_x, posicao_y + 32))

    def _desenhar_pergunta_e_alternativas(self) -> None:
        if self.pergunta_atual is None:
            return

        caixa_pergunta = pygame.Rect(LARGURA_TELA // 2 - 420, 90, 840, 110)
        superficie_caixa = pygame.Surface(caixa_pergunta.size, pygame.SRCALPHA)
        superficie_caixa.fill((10, 10, 20, 200))
        self.tela.blit(superficie_caixa, caixa_pergunta.topleft)
        pygame.draw.rect(self.tela, COR_DESTAQUE, caixa_pergunta, width=2, border_radius=10)

        rotulo_dificuldade = f"[{self.pergunta_atual.materia.upper()} - {self.pergunta_atual.dificuldade.upper()}]"
        texto_rotulo = self.fonte_pequena.render(rotulo_dificuldade, True, COR_AMARELO)
        self.tela.blit(texto_rotulo, (caixa_pergunta.x + 14, caixa_pergunta.y + 8))

        linhas_enunciado = self._quebrar_texto(
            self.pergunta_atual.enunciado, self.fonte_pergunta, caixa_pergunta.width - 28
        )
        for indice, linha in enumerate(linhas_enunciado[:3]):
            texto_linha = self.fonte_pergunta.render(linha, True, COR_BRANCO)
            self.tela.blit(texto_linha, (caixa_pergunta.x + 14, caixa_pergunta.y + 30 + indice * 28))

        letras_em_ordem = ["A", "B", "C", "D"]
        teclas_jogador1 = ["Q", "W", "E", "R"]
        teclas_jogador2 = ["U", "I", "O", "P"]
        largura_alternativa = 380
        altura_alternativa = 56
        posicao_y_alternativas = 230

        for indice, letra in enumerate(letras_em_ordem):
            coluna = indice % 2
            linha_da_grade = indice // 2
            posicao_x = LARGURA_TELA // 2 - largura_alternativa - 10 + coluna * (largura_alternativa + 20)
            posicao_y = posicao_y_alternativas + linha_da_grade * (altura_alternativa + 14)

            caixa_alternativa = pygame.Rect(posicao_x, posicao_y, largura_alternativa, altura_alternativa)
            pygame.draw.rect(self.tela, COR_CINZA, caixa_alternativa, border_radius=8)
            pygame.draw.rect(self.tela, COR_CINZA_CLARO, caixa_alternativa, width=2, border_radius=8)

            texto_alternativa = self.pergunta_atual.obter_texto_alternativa(letra)
            linhas_alternativa = self._quebrar_texto(texto_alternativa, self.fonte_alternativa, largura_alternativa - 24)
            for numero_linha, linha in enumerate(linhas_alternativa[:2]):
                texto_renderizado = self.fonte_alternativa.render(linha, True, COR_BRANCO)
                self.tela.blit(texto_renderizado, (caixa_alternativa.x + 10, caixa_alternativa.y + 4 + numero_linha * 22))

            texto_teclas = f"P1:{teclas_jogador1[indice]} / P2:{teclas_jogador2[indice]}"
            texto_teclas_renderizado = self.fonte_pequena.render(texto_teclas, True, COR_AMARELO)
            self.tela.blit(
                texto_teclas_renderizado,
                (caixa_alternativa.right - texto_teclas_renderizado.get_width() - 8, caixa_alternativa.bottom - 18),
            )

    def _desenhar_cronometro_e_status(self) -> None:
        if self.respostas_habilitadas:
            tempo_restante = max(0.0, TEMPO_LIMITE_RESPOSTA - self.cronometro_resposta)
            texto_cronometro = f"Tempo: {tempo_restante:0.1f}s"
        else:
            texto_cronometro = "Prepare-se..."

        texto_renderizado = self.fonte_hud.render(texto_cronometro, True, COR_DESTAQUE)
        self.tela.blit(texto_renderizado, (LARGURA_TELA // 2 - texto_renderizado.get_width() // 2, 50))

        numero_pergunta_atual = min(
            self.contador_perguntas_respondidas + 1, QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA
        )
        texto_numero_pergunta = self.fonte_pequena.render(
            f"Pergunta {numero_pergunta_atual}/{QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA}",
            True,
            COR_CINZA_CLARO,
        )
        self.tela.blit(texto_numero_pergunta, (LARGURA_TELA // 2 - texto_numero_pergunta.get_width() // 2, 70))

    def desenhar(self) -> None:
        """Desenha o cenário, os personagens e toda a interface da batalha na tela."""
        self.tela.blit(self.cenario_atual, (0, 0))
        self.grupo_personagens.draw(self.tela)

        self._desenhar_painel_jogador(self.jogador1, 40, 40, alinhado_a_direita=False)
        self._desenhar_painel_jogador(self.jogador2, LARGURA_TELA - 40, 40, alinhado_a_direita=True)

        if self.estado_rodada != ESTADO_RODADA_FIM_DE_BATALHA:
            self._desenhar_cronometro_e_status()
            self._desenhar_pergunta_e_alternativas()

    def finalizar_batalha_antecipadamente(self) -> None:
        """Finaliza a batalha por ação do usuário (ex: ESC)."""
        if not self.batalha_finalizada:
            self._finalizar_batalha()