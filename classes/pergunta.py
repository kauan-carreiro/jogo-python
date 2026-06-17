from typing import Dict


class Pergunta:
    """Representa uma pergunta com 4 alternativas (A, B, C, D)."""

    def __init__(
        self,
        identificador: int,
        enunciado: str,
        alternativas: Dict[str, str],
        resposta_correta: str,
        dificuldade: str,
        materia: str,
        descritor: str,
    ) -> None:
        self.identificador = identificador
        self.enunciado = enunciado
        self.alternativas = alternativas  # ex: {"A": "...", "B": "...", "C": "...", "D": "..."}
        self.resposta_correta = resposta_correta.upper()
        self.dificuldade = dificuldade
        self.materia = materia
        self.descritor = descritor

    def verificar_resposta(self, letra_escolhida: str) -> bool:
        """Retorna True se a letra escolhida corresponde à resposta correta."""
        if not letra_escolhida:
            return False
        return letra_escolhida.upper() == self.resposta_correta

    def obter_texto_alternativa(self, letra):
        mapa = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3
        }

        indice = mapa.get(letra.upper())

        if indice is not None and indice < len(self.alternativas):
            return self.alternativas[indice]

        return ""

    def __repr__(self) -> str:
        return (
            f"Pergunta(id={self.identificador}, materia={self.materia}, "
            f"descritor={self.descritor}, dificuldade={self.dificuldade})"
        )
    