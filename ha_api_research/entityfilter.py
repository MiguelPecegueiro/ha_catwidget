import json

with open("response.json", "r", encoding= "utf-8") as f:
    data = json.load(f)

    with open("resultset.md", "w", encoding= "utf-8") as g:
    
        for item in data:  
            g.write(item["entity_id"] + "\n")   

