import re
import logging

# Configure basic logging for observability (Constraint: Auditable and reproducible)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentParser:
    """
    Parses unstructured enterprise documents to extract high-density risk signals
    before passing them to the LLM to preserve token limits.
    """

    @staticmethod
    def extract_item_1a(text: str) -> str:
        """
        Extracts 'Item 1A. Risk Factors' from a raw SEC 10-K text dump.
        Bypasses the Table of Contents by finding the longest match between Item 1A and Item 1B.
        """
        logger.info("Initiating regex extraction for 'Item 1A. Risk Factors'.")
        
        # Regex explanation:
        # re.IGNORECASE : Case-insensitive match for the entire pattern
        # re.DOTALL     : Allows the (.*?) to match across newlines
        # item\s+1a\.?\s+risk\s+factors : Matches "Item 1A. Risk Factors" (allows varying whitespace '\s+' and missing periods '\.?')
        # (.*?) : Capturing all text coming after Item 1A up to the next section
        # item\s+1b\.?\s+unresolved\s+staff\s+comments : Matches the start of the next section allowing to stop when next section is found
        pattern = re.compile(
            r"item\s+1a\.?\s+risk\s+factors(.*?)item\s+1b\.?\s+unresolved\s+staff\s+comments", 
            re.DOTALL | re.IGNORECASE
        )
        
        matches = pattern.findall(text)
        
        if not matches:
            logger.warning("Regex failed to find Item 1A and 1B markers. Falling back to naive chunking.")
            # Fallback: Just return the first 20,000 characters if regex fails
            return text[:20000]
            
        # The longest match is likely the most complete and accurate extraction hence we select it
        # Guarantees that we capture the full Risk Factors section even if there are multiple matches due to formatting inconsistencies
        longest_match = max(matches, key=len)

        
        extracted_text = longest_match.strip()
        logger.info(f"Successfully extracted {len(extracted_text)} characters of Risk Factors.")
        
        # Truncate to a safe token limit for standard LLMs (e.g., ~15,000 words to fit safely in an 8k-16k context window)
        # 1 token is roughly 4 chars, so 60,000 chars is roughly 15,000 tokens.
        max_chars = 60000 
        if len(extracted_text) > max_chars:
            logger.info(f"Truncating extraction from {len(extracted_text)} to {max_chars} characters for token efficiency.")
            extracted_text = extracted_text[:max_chars]
            
        return extracted_text

    @classmethod
    def process_document(cls, file_path: str) -> str:
        """
        Reads a raw file and routes it to the correct extraction strategy.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
                
            logger.info(f"Loaded raw document {file_path} ({len(raw_text)} characters).")
            
            # In a production system, you would check document metadata here to determine 
            # if it's an SEC 10-K, a SOC 2 audit, etc., and apply the right regex.
            # For this assessment, we apply the 10-K extractor.
            filtered_text = cls.extract_item_1a(raw_text)
            
            return filtered_text
            
        except FileNotFoundError:
            logger.error(f"File not found at {file_path}")
            raise


if __name__ == "__main__":
    # Point this to the raw text file you just downloaded
    test_file_path = "data/raw/coinbase_10k.txt"
    
    print(f"Testing extraction on {test_file_path}...")
    
    try:
        extracted_text = DocumentParser.process_document(test_file_path)
        
        print("\n--- EXTRACTION PREVIEW (First 1500 chars) ---")
        print(extracted_text[:1500]) 
        print("\n---------------------------------------------")
        print(f"Total extracted length: {len(extracted_text)} characters.")
        
        # Save the extracted snippet so you can manually review it
        output_path = "data/raw/extracted_item_1a.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"Saved full extraction to {output_path} for review.")
        
    except Exception as e:
        print(f"Extraction failed: {e}")