import requests
from bs4 import BeautifulSoup
from pathlib import Path

def download_sec_filing():
    """Fetches the actual Coinbase 10-K filing from the SEC EDGAR database."""
    
    # The SEC requires a custom User-Agent to prevent scraping blocks. 
    # Use your name and email to comply with their API terms.
    headers = {
        "User-Agent": "Ahmed Naeem Bhuri (ahmednaeembhur456@gmail.com)" 
    }
    
    # URL to the HTML version of Coinbase's 2024 Form 10-K
    url = "https://www.sec.gov/Archives/edgar/data/1679788/000167978824000022/coin-20231231.htm"
    
    print("Fetching Coinbase 10-K from SEC EDGAR...")
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Ensure we raise an error if the request fails rather than passing down empty data along the LLM wasting resources

    # Strips out HTML tags and extracts the text content. The SEC filings are often messy, so we clean up whitespace and line breaks.
    print("Parsing HTML and extracting text...")
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator="\n")
    
    # Clean up massive whitespace gaps common in SEC HTML parsing
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    clean_text = "\n".join(lines)
    
    # Save to local 'raw' directory
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "coinbase_10k.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(clean_text)
        
    print(f"✅ Successfully downloaded {len(clean_text)} characters to {output_path}")

if __name__ == "__main__":
    download_sec_filing()