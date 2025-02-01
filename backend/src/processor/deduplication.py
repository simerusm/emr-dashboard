from difflib import SequenceMatcher

def deduplicate_overlap(native_text: str, ocr_text: str) -> str:
    """
    Deduplicate overlapping text between native extraction and OCR output.
    If both texts share a significant overlap, the duplicate portion is removed from the OCR output before concatenation.
    """
    if not native_text:
        return ocr_text.strip()
    if not ocr_text:
        return native_text.strip()

    native_text = native_text.strip()
    ocr_text = ocr_text.strip()

    if native_text == ocr_text:
        return native_text

    ratio = SequenceMatcher(None, native_text, ocr_text).ratio()
    if ratio > 0.7:
        return native_text if len(native_text) > len(ocr_text) else ocr_text

    def longest_common_substring(s1, s2):
        m = [[0] * (1 + len(s2)) for _ in range(1 + len(s1))]
        longest, x_longest = 0, 0
        for x in range(1, 1 + len(s1)):
            for y in range(1, 1 + len(s2)):
                if s1[x - 1] == s2[y - 1]:
                    m[x][y] = m[x - 1][y - 1] + 1
                    if m[x][y] > longest:
                        longest = m[x][y]
                        x_longest = x
                else:
                    m[x][y] = 0
        return s1[x_longest - longest: x_longest]

    lcs = longest_common_substring(native_text, ocr_text)
    if len(lcs) > 20:
        if ocr_text.startswith(lcs):
            ocr_text = ocr_text[len(lcs):].strip()
        elif ocr_text.endswith(lcs):
            ocr_text = ocr_text[:-len(lcs)].strip()
    
    combined = native_text
    if ocr_text:
        combined += "\n" + ocr_text
    return combined