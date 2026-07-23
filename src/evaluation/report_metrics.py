def average_similarity(
    papers: list
) -> float:

    if not papers:
        return 0

    similarities = [

        1 - paper["distance"]

        for paper in papers

    ]

    return sum(similarities) / len(similarities)