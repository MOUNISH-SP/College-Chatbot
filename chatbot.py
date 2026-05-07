import os
import re
from pinecone import Pinecone

THRESHOLD = 0.25
TOP_K = 5


def rewrite_query(user_query: str) -> str:
    """
    Improve search quality by expanding generic terms.
    """
    q = user_query.lower()

    if "department" in q:
        return user_query + " undergraduate programmes engineering branches BE BTech courses"

    if "course" in q:
        return user_query + " BE BTech programmes offered"

    if "placement" in q:
        return user_query + " placement statistics training companies recruiters"

    if "admission" in q:
        return user_query + " admission process eligibility application"

    return user_query


def clean_text(text: str) -> str:
    import re

    # Remove UI words
    text = re.sub(r"View Department ➝", "", text)
    text = re.sub(r"ck on any course.*", "", text)
    text = re.sub(r"Admission Proces.*", "", text)

    # Split into lines
    lines = text.split()

    # Join back cleanly
    cleaned = " ".join(lines)

    return cleaned.strip()


def main():
    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        print("Set PINECONE_API_KEY first.")
        return

    pc = Pinecone(api_key=api_key)
    index = pc.Index("college-chatbot1")

    print("College Enquiry Chatbot Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        user_question = input("You: ")

        if user_question.lower() == "exit":
            print("Goodbye!")
            break

        if not user_question.strip():
            print("Please enter a question.\n")
            continue

        improved_query = rewrite_query(user_question)

        try:
            results = index.search(
                namespace="__default__",
                query={
                    "inputs": {"text": improved_query},
                    "top_k": TOP_K
                }
            )

            matches = results.get("result", {}).get("hits", [])

            if not matches:
                print("\nNo relevant documents found.\n")
                continue

            best_score = matches[0].get("_score", 0)

            print(f"\nSimilarity Score: {best_score:.4f}")

            if best_score < THRESHOLD:
                print("\nAnswer not found in college documents.\n")
                continue

            print("\nAnswer:\n")

            displayed_sources = set()

            unique_programmes = set()

            for match in matches:
                fields = match.get("fields", {})
                text = fields.get("text", "")

                cleaned = clean_text(text)

                # Extract only BE/BTech programmes
                words = cleaned.split()

                for i in range(len(words)):
                    if words[i] in ["B.E.", "B.Tech", "BTech"]:
                        programme = " ".join(words[i:i+4])
                        unique_programmes.add(programme)

            if unique_programmes:
                print("\nUndergraduate Engineering Programmes:\n")
                for prog in sorted(unique_programmes):
                    print("•", prog)
            else:
                print("\nNo structured programme list found.\n")

            print()

        except Exception as e:
            print(f"Error during search: {e}\n")


if __name__ == "__main__":
    main()
