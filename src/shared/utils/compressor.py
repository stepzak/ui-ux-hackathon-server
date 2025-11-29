from langchain_text_splitters import CharacterTextSplitter


def compress_context(data: dict, max_chars: int = 7000) -> str:
    import json
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if len(text) < max_chars:
        return text

    splitter = CharacterTextSplitter(chunk_size=max_chars, chunk_overlap=200)
    docs = splitter.create_documents([text])
    return docs[0].page_content