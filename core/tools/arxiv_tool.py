import arxiv
from .base_tool import BaseTool


class ArxivTool(BaseTool):
    name = "Arxiv"

    def run(self, query):
        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        results = []

        for paper in client.results(search):
            authors = ", ".join(author.name for author in paper.authors[:3])

            results.append(
                f"Título: {paper.title}\n"
                f"Autores: {authors}\n"
                f"Publicado: {paper.published.date()}\n"
                f"Resumo: {paper.summary[:900]}...\n"
                f"PDF: {paper.pdf_url}"
            )

        if not results:
            return "Nenhum artigo encontrado no arXiv."

        return "\n\n---\n\n".join(results)