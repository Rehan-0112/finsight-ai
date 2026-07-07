import arxiv
import json
import os


queries = [

"revenue forecasting",

"earnings forecasting",

"financial forecasting",

"corporate finance",

"capital structure",

"debt ratio",

"leverage ratio",

"financial statement analysis",

"balance sheet analysis",

"company valuation",

"XGBoost finance",

"Explainable AI Finance",

"Financial NLP",

"LLM finance",

"risk modeling"

]


os.makedirs("data/raw", exist_ok=True)


for query in queries:

    papers = []

    search = arxiv.Search(

        query=query,

        max_results=50,

        sort_by=arxiv.SortCriterion.Relevance

    )

    client = arxiv.Client()

    for result in client.results(search):

        papers.append({

            "title": result.title,

            "authors":

            [a.name for a in result.authors],

            "summary":

            result.summary,

            "published":

            str(result.published),

            "pdf_url":

            result.pdf_url

        })


    filename = query.replace(" ", "_") + ".json"


    path = os.path.join(

        "data/raw",

        filename

    )


    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            papers,

            f,

            indent=4

        )


    print(

        f"Saved {len(papers)} papers to {filename}"

    )