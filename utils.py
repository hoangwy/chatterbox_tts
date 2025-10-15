import re
from typing import List
from configuration import MAX_CHUNK_SIZE

def split_text_by_sentence(text: str) -> List[str]:
    """Given a line of text, split it into chunks of at most MAX_CHUNK_SIZE characters
    at sentence boundaries, forming roughly equal-sized chunks"""
    sentences = text.split(". ")
    n_chunks_needed = len(text) // MAX_CHUNK_SIZE + 1
    approx_chunk_size = len(text) // n_chunks_needed

    chunks = []
    current_chunk = []
    current_length = 0
    for sentence in sentences:
        # Remove excess whitespace like consecutive spaces, newlines, etc.
        sentence = " ".join(sentence.split())
        sentence = sentence.strip()

        if current_length + len(sentence) > approx_chunk_size:
            chunks.append(". ".join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence)

    if current_chunk:
        chunks.append(". ".join(current_chunk))

    # If chunks end with a-z0-9, add a period to the end
    chunks = [chunk + "." if re.match(r"[a-zA-Z0-9]", chunk[-1]) else chunk for chunk in chunks if len(chunk) > 0]

    return chunks


def process_text_file(file_path: str) -> List[str]:
    """Process a text file like benchmark.py does"""
    with open(file_path, "r") as f:
        text = f.read()
    
    # Remove lines starting with #
    text = "\n".join([line for line in text.split("\n") if not line.startswith("#")])

    # Chunk text by newlines
    text = [i.strip() for i in text.split("\n") if len(i.strip()) > 0]

    # Split text into chunks
    text = [split_text_by_sentence(line) for line in text]

    # Flatten list
    text = [item for sublist in text for item in sublist]
    
    return text
