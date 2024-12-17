def create_chunks(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        
        if current_size + word_size > chunk_size:
            # Save current chunk
            chunks.append(" ".join(current_chunk))
            
            # Keep last few words for overlap
            overlap_words = current_chunk[-overlap//10:]  # Approximate words for overlap
            current_chunk = overlap_words + [word]
            current_size = sum(len(w) + 1 for w in current_chunk)
        else:
            current_chunk.append(word)
            current_size += word_size
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks 