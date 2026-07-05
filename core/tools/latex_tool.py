from core.tools.base_tool import BaseTool


class LatexTool(BaseTool):
    name = "Latex"

    def run(self, query):
        text = query.strip()

        return f"""\\documentclass[11pt]{{article}}

\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{amsmath, amssymb, amsthm, mathtools}}
\\usepackage{{hyperref}}

\\newtheorem{{theorem}}{{Teorema}}
\\newtheorem{{lemma}}{{Lema}}
\\newtheorem{{proposition}}{{Proposição}}
\\newtheorem{{corollary}}{{Corolário}}
\\theoremstyle{{definition}}
\\newtheorem{{definition}}{{Definição}}
\\newtheorem{{hypothesis}}{{Hipótese}}

\\title{{Nota de Pesquisa}}
\\author{{Felipe Gaspar}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\section{{Contexto}}

{text}

\\section{{Formulação}}

\\begin{{hypothesis}}
Escrever aqui a hipótese principal.
\\end{{hypothesis}}

\\section{{Estratégia}}

\\begin{{enumerate}}
    \\item Formalizar os objetos centrais.
    \\item Identificar o termo crítico.
    \\item Procurar estimativas coercivas ou cancelamentos.
    \\item Testar contra critérios conhecidos de regularidade.
\\end{{enumerate}}

\\section{{Equações úteis}}

\\begin{{align}}
\\partial_t u + (u \\cdot \\nabla)u &= -\\nabla p + \\nu \\Delta u, \\\\
\\nabla \\cdot u &= 0.
\\end{{align}}

\\section{{Próximos passos}}

\\begin{{itemize}}
    \\item Definir notação.
    \\item Procurar contraexemplos.
    \\item Comparar com Beale--Kato--Majda.
    \\item Registrar conclusão no diário de pesquisa.
\\end{{itemize}}

\\end{{document}}
"""