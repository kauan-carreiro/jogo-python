import json
import random
from typing import Dict, List, Optional, Set, Tuple

from classes.pergunta import Pergunta


class GerenciadorPerguntas:
    """Carrega, organiza e sorteia perguntas a partir de dados/perguntas.json."""

    def __init__(self, caminho_arquivo: str) -> None:
        self.caminho_arquivo = caminho_arquivo
        self.banco_perguntas: Dict = {}
        self.perguntas_usadas_na_partida: Set[Tuple[str, str, str, int]] = set()
        self.carregar_perguntas()

    def carregar_perguntas(self) -> None:
        """Lê o arquivo JSON e armazena toda a estrutura em memória."""
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as arquivo:
                self.banco_perguntas = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError) as erro:
            print(f"[AVISO] Não foi possível carregar perguntas.json: {erro}")
            self.banco_perguntas = {}

    def reiniciar_controle_de_repeticao(self) -> None:
        """Limpa o controle de perguntas já usadas. Deve ser chamado ao iniciar uma nova batalha."""
        self.perguntas_usadas_na_partida = set()

    def _listar_descritores(self, materia: str) -> List[str]:
        """Retorna a lista de descritores cadastrados para uma matéria (ex: D05, D01)."""
        return list(self.banco_perguntas.get(materia, {}).keys())

    def sortear_pergunta(
        self, materia: str, dificuldade: str, descritor: Optional[str] = None
    ) -> Optional[Pergunta]:
        descritores_disponiveis = [descritor] if descritor else self._listar_descritores(materia)
        if not descritores_disponiveis:
            return None

        random.shuffle(descritores_disponiveis)

        for descritor_escolhido in descritores_disponiveis:
            questoes = (
                self.banco_perguntas.get(materia, {})
                .get(descritor_escolhido, {})
                .get(dificuldade, [])
            )
            candidatas = [
                questao
                for questao in questoes
                if (materia, descritor_escolhido, dificuldade, questao["id"])
                not in self.perguntas_usadas_na_partida
            ]
            if candidatas:
                questao_sorteada = random.choice(candidatas)
                chave_unica = (materia, descritor_escolhido, dificuldade, questao_sorteada["id"])
                self.perguntas_usadas_na_partida.add(chave_unica)
                return Pergunta(
                    identificador=questao_sorteada["id"],
                    enunciado=questao_sorteada["enunciado"],
                    alternativas=questao_sorteada["alternativas"],
                    resposta_correta=questao_sorteada["resposta"],
                    dificuldade=dificuldade,
                    materia=materia,
                    descritor=descritor_escolhido,
                )

        return None

    def sortear_pergunta_para_modo(self, modo: str, dificuldade: str) -> Optional[Pergunta]:
        if modo == "mista":
            materia_escolhida = random.choice(["matematica", "portugues"])
        else:
            materia_escolhida = modo
        return self.sortear_pergunta(materia_escolhida, dificuldade)

    def existem_perguntas_disponiveis(self, materia: str) -> bool:
        """Verifica se há ao menos uma pergunta cadastrada para a matéria informada."""
        return bool(self.banco_perguntas.get(materia))
    