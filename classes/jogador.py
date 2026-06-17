from typing import Dict, List, Optional


class Jogador:
    """Guarda vida, pontuação e estatísticas de desempenho de um jogador."""

    def __init__(self, nome: str, mapeamento_teclas: Dict[int, str], vida_inicial: int = 100) -> None:
        self.nome = nome
        self.mapeamento_teclas = mapeamento_teclas
        self.vida = vida_inicial
        self.vida_maxima = vida_inicial

        # Estado referente à rodada (pergunta) atual.
        self.resposta_selecionada: Optional[str] = None
        self.tempo_resposta_atual: Optional[float] = None
        self.ja_respondeu_na_rodada: bool = False

        # Estatísticas acumuladas durante toda a partida.
        self.total_acertos: int = 0
        self.total_erros: int = 0
        self.dano_total_causado: int = 0
        self.lista_tempos_resposta: List[float] = []
        self.ultimo_dano_causado: int = 0

    def reiniciar_para_nova_rodada(self) -> None:
        """Reseta o estado de resposta para que o jogador possa responder a próxima pergunta."""
        self.resposta_selecionada = None
        self.tempo_resposta_atual = None
        self.ja_respondeu_na_rodada = False

    def registrar_resposta(self, letra: str, tempo_resposta: float) -> None:
        """Armazena a alternativa escolhida e o tempo de resposta da rodada atual."""
        self.resposta_selecionada = letra
        self.tempo_resposta_atual = tempo_resposta
        self.ja_respondeu_na_rodada = True
        self.lista_tempos_resposta.append(tempo_resposta)

    def registrar_acerto(self, dano_causado: int) -> None:
        """Atualiza as estatísticas após uma resposta correta."""
        self.total_acertos += 1
        self.dano_total_causado += dano_causado
        self.ultimo_dano_causado = dano_causado

    def registrar_erro(self) -> None:
        """Atualiza as estatísticas após uma resposta incorreta (ou ausência de resposta)."""
        self.total_erros += 1
        self.ultimo_dano_causado = 0

    def receber_dano(self, dano: int) -> None:
        """Reduz a vida do jogador, nunca permitindo um valor negativo."""
        self.vida = max(0, self.vida - dano)

    def esta_derrotado(self) -> bool:
        """Retorna True se a vida do jogador chegou a zero."""
        return self.vida <= 0

    def calcular_tempo_medio(self) -> float:
        """Calcula o tempo médio de resposta do jogador na partida."""
        if not self.lista_tempos_resposta:
            return 0.0
        return sum(self.lista_tempos_resposta) / len(self.lista_tempos_resposta)

    def calcular_melhor_tempo(self) -> float:
        """Retorna o menor tempo de resposta registrado na partida."""
        if not self.lista_tempos_resposta:
            return 0.0
        return min(self.lista_tempos_resposta)

    def calcular_precisao(self) -> float:
        """Calcula o percentual de acertos em relação ao total de perguntas respondidas."""
        total_respondidas = self.total_acertos + self.total_erros
        if total_respondidas == 0:
            return 0.0
        return (self.total_acertos / total_respondidas) * 100

    def obter_letra_pela_tecla(self, tecla: int) -> Optional[str]:
        """Converte o código de uma tecla do pygame na letra de alternativa correspondente."""
        return self.mapeamento_teclas.get(tecla)