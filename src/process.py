import pandas as pd
import re

# product/productId: B001E4KFG0
# review/userId: A3SGXH7AUHU8GW
# review/profileName: delmartian
# review/helpfulness: 1/1
# review/score: 5.0
# review/time: 1303862400
# review/summary: Good Quality Dog Food
# review/text: I have bought several of the Vitality canned dog food products and have found them all to be of good quality. The product looks more like a stew than a processed meat and it smells better. My Labrador is finicky and she appreciates this product better than  most.

#data = pd.DataFrame(columns=["Id", "ProductId", "UserId", "ProfileName", "HelpfulnessNumerator", "HelpfulnessDenominator", "Score", "Time", "Summary", "Text"])
rows = list()

f = open("input/Reviews.txt", encoding="latin-1")
line = f.readline()
review_id = 0

while line != "":
    if line[:7]!="product":
        line=f.readline()
        continue
    review_id += 1
    product_id   = re.findall(r"^product/productId: (.*)\Z",  line, flags=re.DOTALL)[0].strip()
    user_id      = re.findall(r"^review/userId: (.*)\Z",      f.readline(), flags=re.DOTALL)[0].strip()
    profile_name = re.findall(r"^review/profileName: (.*)\Z", f.readline(), flags=re.DOTALL)[0].strip()
    # weird edge cases
    line = f.readline()
    if line[:6] != "review":
        if line[:2]=="88" or line[:11]=="...creative" or line[:6]=="School" or line[:6]=="I am a":
            line = f.readline()
        else:
            print(line)
    helpfulness  = re.findall(r"^review/helpfulness: (.*)\Z", line, flags=re.DOTALL)[0].strip()
    score        = re.findall(r"^review/score: (.*)\Z",       f.readline(), flags=re.DOTALL)[0].strip()
    time         = re.findall(r"^review/time: (.*)\Z",        f.readline(), flags=re.DOTALL)[0].strip()
    summary      = re.findall(r"^review/summary: (.*)\Z",     f.readline(), flags=re.DOTALL)[0].strip()
    text         = re.findall(r"^review/text: (.*)\Z",        f.readline(), flags=re.DOTALL)[0].strip()
    line = f.readline()

    helpfulness_numerator, helpfulness_denominator = helpfulness.split("/")
    helpfulness_numerator = int(helpfulness_numerator)
    helpfulness_denominator = int(helpfulness_denominator)
    score = float(score)
    time = int(time)

    row = [review_id, product_id, user_id, profile_name, helpfulness_numerator, helpfulness_denominator, score, time, summary, text]
    rows.append(row)

data = pd.DataFrame(rows, columns=["Id", "ProductId", "UserId", "ProfileName", "HelpfulnessNumerator", "HelpfulnessDenominator", "Score", "Time", "Summary", "Text"])
print(data)

conversion = {
    "object": "TEXT",
    "float64": "NUMERIC",
    "int64": "INTEGER"
}

sql = """.separator ","

CREATE TABLE Reviews (
%s);

.import "working/noHeader/Reviews.csv" Reviews
""" % ",\n".join(["    %s %s%s" % (key,
                                   conversion[str(data.dtypes[key])],
                                   " PRIMARY KEY" if key=="Id" else "")
                  for key in data.dtypes.keys()])

data.to_csv("output/Reviews.csv", index=False)

open("working/import.sql", "w").write(sql)
