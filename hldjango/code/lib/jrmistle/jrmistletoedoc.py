from mistletoe import Document, block_token, HTMLRenderer
#from mistletoe import Document, ParseContext, token_sets


# THIS IS SO FUCKING EVIL, due to mistletoe markdown doing weird things with leading ~~~~ which we uses 

class JrFixedMistletoeDocument(Document):
    """
    A mistletoe Document that parses everything except fenced-code blocks.
    """

    def __init__(self, source, *args, **kwargs):
        # --- 1.  copy the original global list -----------------------------
        original_tokens = list(block_token._token_types)

        # --- 2.  drop CodeFence from that list ------------------------------
        block_token._token_types = [
            tok for tok in original_tokens if tok.__name__ != "CodeFence"
        ]  # ←  CodeFence is gone

        try:
            # --- 3.  let the normal Document constructor run ----------------
            super().__init__(source, *args, **kwargs)
        finally:
            # --- 4.  ALWAYS restore the global list -------------------------
            block_token._token_types = original_tokens