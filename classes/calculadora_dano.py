from classes.constantes import (
    BONUS_PRIMEIRA_RESPOSTA_CORRETA,
    FAIXA_TEMPO_MEDIA,
    FAIXA_TEMPO_RAPIDA,
    TABELA_DANO,
)


class CalculadoraDano:
    """Encapsula a fórmula de dano do jogo (acerto + velocidade + dificuldade)."""

    @staticmethod
    def _obter_faixa_de_tempo(tempo_resposta: float) -> str:
        if tempo_resposta <= FAIXA_TEMPO_RAPIDA:
            return "rapida"
        if tempo_resposta <= FAIXA_TEMPO_MEDIA:
            return "media"
        return "lenta"

    @staticmethod
    def calcular_dano(
        resposta_correta: bool,
        dificuldade: str,
        tempo_resposta: float,
        foi_o_primeiro_a_acertar: bool = False,
    ) -> int:
        if not resposta_correta:
            return 0

        faixa_de_tempo = CalculadoraDano._obter_faixa_de_tempo(tempo_resposta)
        tabela_da_dificuldade = TABELA_DANO.get(dificuldade, TABELA_DANO["normal"])
        dano_base = tabela_da_dificuldade.get(faixa_de_tempo, 0)

        dano_total = dano_base
        if foi_o_primeiro_a_acertar:
            dano_total += BONUS_PRIMEIRA_RESPOSTA_CORRETA

        return dano_total