import os
from pinecone import Pinecone


def main():
    # Get API key from environment variable
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    if not PINECONE_API_KEY:
        print("ERROR: Please set PINECONE_API_KEY environment variable.")
        return

    # Connect to Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("college-chatbot1")

    print("College Chatbot Query System Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        user_question = input("You: ")

        if user_question.lower() == "exit":
            print("Exiting chatbot.")
            break

        try:
            # Use integrated embedding search
            results = index.search(
                namespace="__default__",
                query={
                    "inputs": {"text": user_question},
                    "top_k": 3
                }
            )

            matches = results.get("result", {}).get("hits", [])

            if not matches:
                print("No matches found.\n")
                continue

            print("\nTop Matches:\n")

            for match in matches:
                score = match.get("_score", 0)
                metadata = match.get("fields", {})

                source = metadata.get("source_filename", "Unknown")
                text = metadata.get("text", "")

                print("--------------------------------------------------")
                print(f"Score: {score:.4f}")
                print(f"Source: {source}")
                print("Text Preview:")
                print(text[:300])  # Show first 300 characters
                print("--------------------------------------------------\n")

        except Exception as e:
            print(f"Error during search: {e}\n")


if __name__ == "__main__":
    main()
