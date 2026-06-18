import os
import random
from typing import List, Optional, Tuple

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
    TEMPO_CONTAGEM_REGRESSIVA,
    TEMPO_EXIBICAO_GO,
    TEMPO_EXIBICAO_DANO,
    TECLA_TELA_CONTROLES,
)
from classes.gerenciador_cenarios import GerenciadorCenarios
from classes.gerenciador_perguntas import GerenciadorPerguntas
from classes.gerenciador_sons import GerenciadorSons
from classes.jogador import Jogador
from classes.personagem import Personagem, ESTADO_ERRO
from classes.tela_controles import TelaControles

# Estados da rodada (adicionamos CONTAGEM)
ESTADO_RODADA_CONTAGEM = "contagem"
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
        self.estado_rodada = ESTADO_RODADA_CONTAGEM  # <-- começa com contagem
        self.respostas_habilitadas = False
        self.cronometro_rodada = 0.0
        self.cronometro_resposta = 0.0
        self.cronometro_resultado = 0.0
        self.alguem_acertou_primeiro_na_rodada = False
        self.contador_perguntas_respondidas = 0
        self.tempo_total_batalha = 0.0
        self.vencedor: Optional[Jogador] = None
        self.batalha_finalizada = False

        # --- NOVOS ATRIBUTOS PARA CONTAGEM REGRESSIVA ---
        self.contagem_atual = 3
        self.cronometro_contagem = 0.0
        self.mostrar_go = False
        self.cronometro_go = 0.0

        # --- MENSAGENS FLUTUANTES (DANO) ---
        self.mensagens: List[Tuple[str, Tuple[int, int], Tuple[int, int, int], float]] = []

        # --- FONTE MAIOR PARA O CRONÔMETRO ---
        self.fonte_cronometro = pygame.font.SysFont("segoe ui", 48, bold=True)

        # Demais fontes
        self.fonte_pergunta = pygame.font.SysFont("segoe ui", 26, bold=True)
        self.fonte_alternativa = pygame.font.SysFont("segoe ui", 22)
        self.fonte_hud = pygame.font.SysFont("segoe ui", 22, bold=True)
        self.fonte_pequena = pygame.font.SysFont("segoe ui", 18)
        self.fonte_contagem = pygame.font.SysFont("segoe ui", 120, bold=True)
        self.fonte_vencedor = pygame.font.SysFont("segoe ui", 80, bold=True)

        # --- ÁUDIO ---
        self.gerenciador_sons.tocar_musica_de_batalha()

        # --- TELA DE CONTROLES (overlay com as teclas de cada jogador) ---
        self.tela_controles = TelaControles(self.tela)
        # Antes da primeira rodada de toda batalha, mostramos a tela de
        # controles automaticamente. Ela só fecha quando o jogador pressionar
        # a tecla TECLA_TELA_CONTROLES (F1) — mesma tecla usada para
        # abri-la/fechá-la a qualquer momento durante a batalha.
        self.mostrando_tela_controles = True

        # Inicia a primeira rodada com contagem
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
        """Sorteia uma nova pergunta, reinicia estado e inicia contagem regressiva."""
        dificuldade_sorteada = self._escolher_dificuldade_aleatoria()
        pergunta_sorteada = self.gerenciador_perguntas.sortear_pergunta_para_modo(
            self.modo_jogo, dificuldade_sorteada
        )

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

        # Inicia contagem regressiva
        self.estado_rodada = ESTADO_RODADA_CONTAGEM
        self.contagem_atual = 3
        self.cronometro_contagem = 0.0
        self.mostrar_go = False
        self.cronometro_go = 0.0
        self.respostas_habilitadas = False
        self.alguem_acertou_primeiro_na_rodada = False
        self.cronometro_rodada = 0.0
        self.cronometro_resposta = 0.0

    def _processar_resposta_jogador(
        self,
        jogador: Jogador,
        oponente: Jogador,
        personagem_jogador: Personagem,
        personagem_oponente: Personagem,
        letra: str,
    ) -> None:
        """Processa a escolha de alternativa: calcula dano, exibe mensagem e animações."""
        if jogador.ja_respondeu_na_rodada or not self.respostas_habilitadas:
            return

        tempo_resposta = self.cronometro_resposta
        jogador.registrar_resposta(letra, tempo_resposta)

        resposta_correta = self.pergunta_atual.verificar_resposta(letra)
        foi_o_primeiro_a_acertar = resposta_correta and not self.alguem_acertou_primeiro_na_rodada
        if resposta_correta:
            self.alguem_acertou_primeiro_na_rodada = True

        dano_causado = CalculadoraDano.calcular_dano(
            resposta_correta,
            self.pergunta_atual.dificuldade,
            tempo_resposta,
            foi_o_primeiro_a_acertar,
        )

        if resposta_correta:
            jogador.registrar_acerto(dano_causado)
            oponente.receber_dano(dano_causado)
            personagem_jogador.iniciar_animacao_ataque()
            personagem_oponente.iniciar_animacao_dano()
            self.gerenciador_sons.tocar_efeito("ataque")
            self.gerenciador_sons.tocar_efeito("dano")

            # Exibe dano flutuante no oponente
            self._adicionar_mensagem_dano(
                f"-{dano_causado}",
                personagem_oponente.rect.centerx,
                personagem_oponente.rect.top - 20,
                COR_VERMELHO
            )
        else:
            jogador.registrar_erro()
            # Anima erro no personagem que errou
            personagem_jogador.iniciar_animacao_erro()
            self.gerenciador_sons.tocar_efeito("erro")  # Opcional, adicione um som de erro

    def _adicionar_mensagem_dano(self, texto: str, x: int, y: int, cor: Tuple[int, int, int]) -> None:
        """Adiciona uma mensagem flutuante de dano na tela."""
        self.mensagens.append((texto, (x, y), cor, TEMPO_EXIBICAO_DANO))

    def processar_evento(self, evento: pygame.event.Event) -> None:
        """Processa eventos de teclado: abertura/fechamento da tela de
        controles e seleção de alternativas pelos dois jogadores."""
        if evento.type != pygame.KEYDOWN:
            return

        # A tecla de controles funciona como um interruptor (toggle) e tem
        # prioridade sobre qualquer outra coisa, podendo ser usada em
        # qualquer momento da batalha (inclusive durante a contagem ou
        # exibição de resultado).
        if evento.key == TECLA_TELA_CONTROLES:
            self.mostrando_tela_controles = not self.mostrando_tela_controles
            return

        # Enquanto a tela de controles estiver aberta, o jogo fica pausado:
        # nenhuma resposta é processada.
        if self.mostrando_tela_controles:
            return

        if self.estado_rodada != ESTADO_RODADA_AGUARDANDO_RESPOSTAS:
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
            for jogador in (self.jogador1, self.jogador2):
                if not jogador.ja_respondeu_na_rodada:
                    jogador.ja_respondeu_na_rodada = True
                    jogador.registrar_erro()
                    # Animação de erro para quem não respondeu
                    if jogador is self.jogador1:
                        self.personagem1.iniciar_animacao_erro()
                    else:
                        self.personagem2.iniciar_animacao_erro()

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

        if self.jogador1.total_acertos != self.jogador2.total_acertos:
            return self.jogador1 if self.jogador1.total_acertos > self.jogador2.total_acertos else self.jogador2

        tempo_medio_jogador1 = self.jogador1.calcular_tempo_medio() or float("inf")
        tempo_medio_jogador2 = self.jogador2.calcular_tempo_medio() or float("inf")
        if tempo_medio_jogador1 == tempo_medio_jogador2:
            return None
        return self.jogador1 if tempo_medio_jogador1 < tempo_medio_jogador2 else self.jogador2

    def _finalizar_batalha(self) -> None:
        """Encerra a batalha, define o vencedor e para a música de fundo."""
        self.estado_rodada = ESTADO_RODADA_FIM_DE_BATALHA
        self.batalha_finalizada = True
        self.vencedor = self._determinar_vencedor()

        self.gerenciador_sons.parar_musica()
        self.gerenciador_sons.tocar_efeito("vitoria")

    def obter_dados_resultado(self) -> dict:
        """Consolida as estatísticas finais da batalha."""
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
        """Atualiza o estado da rodada, animações, cronômetros e mensagens."""
        if self.batalha_finalizada:
            return

        # Enquanto a tela de controles estiver aberta (seja a exibição
        # automática do início da batalha, seja por F1 durante o jogo),
        # tudo fica congelado: cronômetro, animações e contagem regressiva.
        if self.mostrando_tela_controles:
            return

        self.tempo_total_batalha += tempo_decorrido
        self.grupo_personagens.update(tempo_decorrido)

        # --- Atualiza mensagens flutuantes (remove as que expiraram) ---
        novas_mensagens = []
        for msg in self.mensagens:
            texto, pos, cor, tempo_restante = msg
            novo_tempo = tempo_restante - tempo_decorrido
            if novo_tempo > 0:
                novas_mensagens.append((texto, pos, cor, novo_tempo))
            # se expirou, descarta
        self.mensagens = novas_mensagens

        # --- Lógica da rodada ---
        if self.estado_rodada == ESTADO_RODADA_CONTAGEM:
            self.cronometro_contagem += tempo_decorrido
            if not self.mostrar_go:
                if self.cronometro_contagem >= TEMPO_CONTAGEM_REGRESSIVA:
                    self.contagem_atual -= 1
                    self.cronometro_contagem = 0.0
                    if self.contagem_atual <= 0:
                        self.mostrar_go = True
                        self.cronometro_go = 0.0
            else:
                self.cronometro_go += tempo_decorrido
                if self.cronometro_go >= TEMPO_EXIBICAO_GO:
                    # Passa para aguardar respostas
                    self.estado_rodada = ESTADO_RODADA_AGUARDANDO_RESPOSTAS
                    self.respostas_habilitadas = True
                    self.cronometro_resposta = 0.0
                    self.cronometro_rodada = 0.0

        elif self.estado_rodada == ESTADO_RODADA_AGUARDANDO_RESPOSTAS:
            self.cronometro_rodada += tempo_decorrido
            if self.respostas_habilitadas:
                self.cronometro_resposta += tempo_decorrido
                self._verificar_fim_da_rodada()

        elif self.estado_rodada == ESTADO_RODADA_EXIBINDO_RESULTADO:
            self.cronometro_resultado += tempo_decorrido
            if self.cronometro_resultado >= TEMPO_EXIBICAO_RESULTADO_RODADA:
                houve_derrota = self.jogador1.esta_derrotado() or self.jogador2.esta_derrotado()
                atingiu_limite = self.contador_perguntas_respondidas >= QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA
                if houve_derrota or atingiu_limite:
                    self._finalizar_batalha()
                else:
                    self._iniciar_nova_rodada()

    # ----------------------------------------------------------------- #
    # DESENHO / INTERFACE
    # ----------------------------------------------------------------- #
    def _quebrar_texto(self, texto: str, fonte: pygame.font.Font, largura_maxima: int) -> List[str]:
        """Quebra um texto em múltiplas linhas."""
        palavras = texto.split(" ")
        linhas: List[str] = []
        linha_atual = ""
        for palavra in palavras:
            linha_teste = f"{linha_atual} {palavra}".strip()
            if fonte.size(linha_teste)[0] <= largura_maxima:
                linha_atual = linha_teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def _desenhar_texto_com_fundo(
        self,
        texto: str,
        fonte: pygame.font.Font,
        pos_x: int,
        pos_y: int,
        cor_texto: Tuple[int, int, int] = COR_BRANCO,
        cor_fundo: Tuple[int, int, int, int] = (0, 0, 0, 140),
        padding_x: int = 6,
        padding_y: int = 3,
        alinhado_direita: bool = False,
        alinhado_centro: bool = False,
    ) -> None:
        """
        Desenha um texto com fundo semitransparente e sombra leve, garantindo
        boa legibilidade independentemente da cor do cenário ao fundo.
        """
        texto_renderizado = fonte.render(texto, True, cor_texto)
        sombra_renderizada = fonte.render(texto, True, (0, 0, 0))

        if alinhado_centro:
            pos_final_x = pos_x - texto_renderizado.get_width() // 2
        elif alinhado_direita:
            pos_final_x = pos_x - texto_renderizado.get_width()
        else:
            pos_final_x = pos_x

        caixa_fundo = pygame.Rect(
            pos_final_x - padding_x,
            pos_y - padding_y,
            texto_renderizado.get_width() + padding_x * 2,
            texto_renderizado.get_height() + padding_y * 2,
        )
        superficie_fundo = pygame.Surface(caixa_fundo.size, pygame.SRCALPHA)
        superficie_fundo.fill(cor_fundo)
        self.tela.blit(superficie_fundo, caixa_fundo.topleft)

        self.tela.blit(sombra_renderizada, (pos_final_x + 1, pos_y + 1))
        self.tela.blit(texto_renderizado, (pos_final_x, pos_y))

    def _desenhar_barra_de_vida(self, jogador: Jogador, pos_x: int, pos_y: int) -> None:
        largura_barra = 320
        altura_barra = 30
        proporcao = max(0.0, jogador.vida / jogador.vida_maxima)

        # Fundo
        pygame.draw.rect(self.tela, COR_CINZA, (pos_x, pos_y, largura_barra, altura_barra), border_radius=8)

        # Cor da vida
        if proporcao > 0.4:
            cor_vida = COR_VERDE
        elif proporcao > 0.15:
            cor_vida = COR_AMARELO
        else:
            cor_vida = COR_VERMELHO

        pygame.draw.rect(
            self.tela,
            cor_vida,
            (pos_x, pos_y, int(largura_barra * proporcao), altura_barra),
            border_radius=8,
        )
        pygame.draw.rect(self.tela, COR_BRANCO, (pos_x, pos_y, largura_barra, altura_barra), width=2, border_radius=8)

        # Texto centralizado
        texto = self.fonte_hud.render(f"{jogador.vida}/{jogador.vida_maxima}", True, COR_BRANCO)
        self.tela.blit(texto, (pos_x + largura_barra // 2 - texto.get_width() // 2, pos_y + 4))

    def _desenhar_painel_jogador(self, jogador: Jogador, pos_x: int, pos_y: int, alinhado_direita: bool) -> None:
        nome = self.fonte_hud.render(jogador.nome, True, COR_DESTAQUE)
        if alinhado_direita:
            self.tela.blit(nome, (pos_x - nome.get_width(), pos_y - 30))
        else:
            self.tela.blit(nome, (pos_x, pos_y - 30))

        barra_x = pos_x if not alinhado_direita else pos_x - 320
        self._desenhar_barra_de_vida(jogador, barra_x, pos_y)

        # Texto de Acertos/Erros/Último dano com fundo + sombra para alta legibilidade
        info = f"Acertos: {jogador.total_acertos}  Erros: {jogador.total_erros}  Último dano: {jogador.ultimo_dano_causado}"
        self._desenhar_texto_com_fundo(
            info,
            self.fonte_pequena,
            pos_x,
            pos_y + 40,
            cor_texto=COR_BRANCO,
            alinhado_direita=alinhado_direita,
        )

    def _desenhar_pergunta_e_alternativas(self) -> None:
        if self.pergunta_atual is None:
            return

        # Deslocamento vertical geral do bloco de pergunta + alternativas.
        # Aumente este valor para descer mais; diminua (ou zere) para subir.
        DESLOCAMENTO_VERTICAL_BLOCO_PERGUNTA = 28

        # Caixa da pergunta
        caixa = pygame.Rect(
            LARGURA_TELA // 2 - 420,
            90 + DESLOCAMENTO_VERTICAL_BLOCO_PERGUNTA,
            840,
            120,
        )
        s = pygame.Surface(caixa.size, pygame.SRCALPHA)
        s.fill((10, 10, 30, 220))
        self.tela.blit(s, caixa.topleft)
        pygame.draw.rect(self.tela, COR_DESTAQUE, caixa, width=2, border_radius=12)

        # Rótulo dificuldade
        rotulo = f"[{self.pergunta_atual.materia.upper()} - {self.pergunta_atual.dificuldade.upper()}]"
        texto_rotulo = self.fonte_pequena.render(rotulo, True, COR_AMARELO)
        self.tela.blit(texto_rotulo, (caixa.x + 14, caixa.y + 8))

        # Enunciado
        linhas = self._quebrar_texto(self.pergunta_atual.enunciado, self.fonte_pergunta, caixa.width - 28)
        for i, linha in enumerate(linhas[:3]):
            texto_linha = self.fonte_pergunta.render(linha, True, COR_BRANCO)
            self.tela.blit(texto_linha, (caixa.x + 14, caixa.y + 32 + i * 30))

        # Alternativas
        letras = ["A", "B", "C", "D"]
        larg_alt = 300
        alt_alt = 60
        y_alt = 200 + DESLOCAMENTO_VERTICAL_BLOCO_PERGUNTA

        for i, letra in enumerate(letras):
            coluna = i % 2
            linha_grade = i // 2
            x = LARGURA_TELA // 2 - larg_alt - 10 + coluna * (larg_alt + 20)
            y = y_alt + linha_grade * (alt_alt + 14)

            rect = pygame.Rect(x, y, larg_alt, alt_alt)
            pygame.draw.rect(self.tela, COR_CINZA, rect, border_radius=10)
            pygame.draw.rect(self.tela, COR_CINZA_CLARO, rect, width=2, border_radius=10)

            texto_alt = self.pergunta_atual.obter_texto_alternativa(letra)
            linhas_alt = self._quebrar_texto(texto_alt, self.fonte_alternativa, larg_alt - 24)
            for j, linha in enumerate(linhas_alt[:2]):
                txt = self.fonte_alternativa.render(linha, True, COR_BRANCO)
                self.tela.blit(txt, (rect.x + 10, rect.y + 6 + j * 24))

    def _desenhar_cronometro_e_status(self) -> None:
        # Cronômetro grande
        if self.respostas_habilitadas:
            tempo_restante = max(0.0, TEMPO_LIMITE_RESPOSTA - self.cronometro_resposta)
            texto_cron = f"{tempo_restante:.1f}s"
            cor = COR_VERDE if tempo_restante > 3 else COR_AMARELO if tempo_restante > 1 else COR_VERMELHO
        else:
            texto_cron = "Prepare-se..."
            cor = COR_BRANCO

        txt_cron = self.fonte_cronometro.render(texto_cron, True, cor)
        self.tela.blit(txt_cron, (LARGURA_TELA // 2 - txt_cron.get_width() // 2, 12))

        # Número da pergunta (com fundo + sombra para destacar sobre o cenário)
        num_pergunta = min(self.contador_perguntas_respondidas + 1, QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA)
        self._desenhar_texto_com_fundo(
            f"Pergunta {num_pergunta}/{QUANTIDADE_MAXIMA_PERGUNTAS_POR_BATALHA}",
            self.fonte_pequena,
            LARGURA_TELA // 2,
            65,
            cor_texto=COR_BRANCO,
            alinhado_centro=True,
        )

        # Dica discreta de como reabrir a tela de controles a qualquer momento
        nome_tecla_overlay = pygame.key.name(TECLA_TELA_CONTROLES).upper()
        self._desenhar_texto_com_fundo(
            f"{nome_tecla_overlay}: Controles",
            self.fonte_pequena,
            LARGURA_TELA - 20,
            ALTURA_TELA - 32,
            cor_texto=COR_CINZA_CLARO,
            alinhado_direita=True,
        )
        

    def _desenhar_contagem_regressiva(self) -> None:
        """Desenha a contagem regressiva (3,2,1,GO!) no centro da tela."""
        if self.estado_rodada != ESTADO_RODADA_CONTAGEM:
            return

        centro_x = LARGURA_TELA // 2
        centro_y = ALTURA_TELA // 2

        if self.mostrar_go:
            texto = "GO!"
            cor = COR_VERDE
        else:
            texto = str(self.contagem_atual) if self.contagem_atual > 0 else "GO!"
            cor = COR_DESTAQUE if self.contagem_atual > 0 else COR_VERDE

        txt = self.fonte_contagem.render(texto, True, cor)
        # Sombra
        sombra = self.fonte_contagem.render(texto, True, (0, 0, 0))
        self.tela.blit(sombra, (centro_x - txt.get_width() // 2 + 4, centro_y - txt.get_height() // 2 + 4))
        self.tela.blit(txt, (centro_x - txt.get_width() // 2, centro_y - txt.get_height() // 2))

    def _desenhar_mensagens_dano(self) -> None:
        """Desenha todas as mensagens flutuantes de dano."""
        for texto, pos, cor, _ in self.mensagens:
            txt = self.fonte_cronometro.render(texto, True, cor)  # usa fonte grande
            self.tela.blit(txt, (pos[0] - txt.get_width() // 2, pos[1]))

    def _desenhar_vencedor_final(self) -> None:
        """Exibe o vencedor na tela antes de ir para o resultado."""
        if not self.batalha_finalizada:
            return
        if self.vencedor is None:
            texto = "EMPATE!"
            cor = COR_DESTAQUE
        else:
            texto = f"{self.vencedor.nome.upper()} VENCEU!"
            cor = COR_VERDE if self.vencedor is self.jogador1 else COR_VERMELHO

        txt = self.fonte_vencedor.render(texto, True, cor)
        sombra = self.fonte_vencedor.render(texto, True, (0, 0, 0))
        centro_x = LARGURA_TELA // 2
        centro_y = ALTURA_TELA // 2
        self.tela.blit(sombra, (centro_x - txt.get_width() // 2 + 4, centro_y - txt.get_height() // 2 + 4))
        self.tela.blit(txt, (centro_x - txt.get_width() // 2, centro_y - txt.get_height() // 2))

    def desenhar(self) -> None:
        """Desenha toda a tela da batalha."""
        self.tela.blit(self.cenario_atual, (0, 0))
        self.grupo_personagens.draw(self.tela)

        # Painéis dos jogadores
        self._desenhar_painel_jogador(self.jogador1, 40, 40, alinhado_direita=False)
        self._desenhar_painel_jogador(self.jogador2, LARGURA_TELA - 40, 40, alinhado_direita=True)

        # Mensagens de dano
        self._desenhar_mensagens_dano()

        # Contagem regressiva
        self._desenhar_contagem_regressiva()

        # Se a batalha não acabou, desenha pergunta, alternativas e cronômetro
        if self.estado_rodada != ESTADO_RODADA_FIM_DE_BATALHA:
            self._desenhar_cronometro_e_status()
            self._desenhar_pergunta_e_alternativas()
        else:
            # Mostra o vencedor na tela final antes de transicionar
            self._desenhar_vencedor_final()

        # A tela de controles é desenhada por último, cobrindo tudo o mais.
        if self.mostrando_tela_controles:
            self.tela_controles.desenhar()

    def finalizar_batalha_antecipadamente(self) -> None:
        """Finaliza a batalha por ação do usuário (ESC)."""
        if not self.batalha_finalizada:
            self._finalizar_batalha()