
import sys

args = sys.argv

if(len(args) > 1):
    arg = sys.argv[1]
else: 
    arg = "";

with open("resultset.md","r",encoding="utf-8") as f:
    lines =  f.readlines()


with open("finalset.md", "w", encoding= "utf-8") as g:
    for item in lines:
        if(arg in item):
            g.write(item)
    