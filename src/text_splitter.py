from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """
    Dynamically split documents based on document size.

    Small PDFs  -> very few or no chunks
    Medium PDFs -> large chunks
    Large PDFs  -> smaller chunks
    """

    total_pages = len(documents)

    total_chars = sum(
        len(doc.page_content)
        for doc in documents
    )

    print("\n========== DOCUMENT ANALYSIS ==========")
    print(f"Pages: {total_pages}")
    print(f"Characters: {total_chars}")
    print("=======================================\n")

    # ---------- Dynamic Chunk Strategy ----------

    if total_pages <= 2 or total_chars <= 5000:

        # Resume / certificate / short report
        chunk_size = total_chars + 500
        chunk_overlap = 0

    elif total_pages <= 10:

        # Medium reports
        chunk_size = 1200
        chunk_overlap = 150

    elif total_pages <= 30:

        # Long reports
        chunk_size = 1000
        chunk_overlap = 150

    else:

        # Books / manuals
        chunk_size = 800
        chunk_overlap = 200

    print("Chunk Strategy")
    print(f"chunk_size    = {chunk_size}")
    print(f"chunk_overlap = {chunk_overlap}\n")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[
            "\n\n",
            "\n",
            " ",
            ""
        ],
    )

    split_docs = splitter.split_documents(documents)

    print(
        f"Split {len(documents)} pages into {len(split_docs)} chunks"
    )

    return split_docs