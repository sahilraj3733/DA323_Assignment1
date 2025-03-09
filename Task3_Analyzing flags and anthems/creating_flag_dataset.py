import json
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random

json_file_path = "countries.json" 

flags_folder = "new_image" 
anthem_folder = "anthems" 

with open(json_file_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

data = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

selected_items = random.sample(list(json_data.items()), 150)
for i, (code, country) in enumerate(selected_items):
    lowercase_code = code.lower()
    
    flag_path = os.path.join(flags_folder, f"{lowercase_code}.jpg")  
    anthem_path = os.path.join(anthem_folder, f"{lowercase_code}.mp3")

    anthem_url = f"https://nationalanthems.info/{lowercase_code}.mp3"
    anthem_response = requests.get(anthem_url,stream=True,headers=headers)
    if anthem_response.status_code == 200:
        with open(anthem_path, "wb") as file:
            file.write(anthem_response.content)
    else:
        anthem_path = None 

    anthem_text = ""
    url = f"https://nationalanthems.info/{lowercase_code}.htm"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        english_translation_div = soup.find(lambda tag: tag.name == "div" and tag.get("title") in ["English lyrics", "English translation"])


        if english_translation_div:
            anthem_div = english_translation_div.find_next_sibling("div")

            if anthem_div:
                inner_div = anthem_div.find("div", align="left")
                if inner_div:
                    for tag in inner_div.find_all():
                        if tag.name != "br":
                            tag.decompose() 

                    for br in inner_div.find_all("br"):
                        br.decompose()

                    anthem_text = " ".join(inner_div.stripped_strings)

    
    print(i,lowercase_code, country, anthem_text,flag_path, anthem_path, "\n\n")
    data.append([lowercase_code, country, anthem_text, flag_path, anthem_path])

df = pd.DataFrame(data, columns=["country_code", "country_name", "anthem_text", "flag_path", "anthem_path"])
df = df.dropna()
df = df.reset_index(drop=True)

csv_path = "countries_with_flags_and_anthems.csv"
df.to_csv(csv_path, index=False)

print(f"CSV file saved at: {csv_path}")
