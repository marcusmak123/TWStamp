import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://law.dot.gov.tw/law-en/home.jsp?id=5&parentpath=0,2&mcustomize=law_list.jsp&lawname=201803090361"
text = requests.get(url)

def taxcheck():
    soup = BeautifulSoup(text.content, "html.parser")
    indicator = "% for shares or share certificates embodying the right to shares issued by companies."
    target_element = soup.find(string=lambda s: indicator in str(s))

    if target_element:
        parent = target_element.parent
        full_text = parent.get_text()

        # Split around the indicator
        parts = full_text.split(indicator)
        if len(parts) < 2:
            return None
        
        left_side = parts[0]

        # Split again at "1." to remove the legal marker
        if "1." in left_side:
            split_parts = left_side.split("1.")
            number_text = split_parts[-1].strip()
            try:
                return float(number_text)
            except ValueError:
                return None

    return None

def update():
    current_rate = taxcheck()
    if current_rate is None:
        print("Rate scrape failed")
        return
    
    current_ym = datetime.now().strftime("%Y-%-m")  
    
    try:
        df = pd.read_csv("twtax.csv")
    except FileNotFoundError:
        print("File can't be found, please fix- Marcus")
    
   
    df[current_ym] = [f"{current_rate}%"]
    
    # Save (will automatically add new columns for new months)
    df.to_csv("twtax.csv", index=False)
    print(f"Updated {current_ym}: {current_rate}%")

if __name__ == "__main__":
    update()
    