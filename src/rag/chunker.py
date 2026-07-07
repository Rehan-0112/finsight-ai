import json
import os

def load_papers():

    documents = []

    folder = "data/raw"

    for file in os.listdir(folder):

        if file.endswith(".json"):

            path = os.path.join(folder,file)

            with open(path,"r",encoding="utf-8") as f:

                papers = json.load(f)

            for paper in papers:

                document = {

                "text": f"""
                Title:
                {paper['title']}

                Authors:
                {', '.join(paper['authors'])}

                Published:
                {paper['published']}

                Abstract:
                {paper['summary']}
                """,

                "metadata": {

                "title": paper["title"],

                "authors": ", ".join(paper["authors"]),

                "published": paper["published"],

                "pdf_url": paper["pdf_url"]

                }

                }

                documents.append(document)

    return documents


documents = load_papers()

print("Documents Loaded:",len(documents))

print()

print("Example Document:")

print()

print(documents[0])