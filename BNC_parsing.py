#BNCの全データを構文解析してジャンル別に保存
import xml.etree.ElementTree as ET
import os
import re
import stanza
import datetime


nlp = stanza.Pipeline('en')
os.chdir(r"E:\program\BNC_parse")

#元のファイルのXMLを解析
tree = ET.parse("whole_BNC.xml")
root = tree.getroot()

#ファイルIDごとにテキストを取得して解析してbinary dataで保存---------------------------------
attrib_list = [child.attrib for child in root]   
for attrib in attrib_list:
    id, genre = attrib.values()
    text = root.findtext(f'./doc[@id="{id}"][@genre="{genre}"]')
    text = re.sub(r'\n', r'\n\n', text)
    text = re.sub(r'\n\n+', r'\n\n', text)
    #テキストを解析
    doc = nlp(text)
    
    #parseしたデータが入ったdocumentオブジェクトをbinary dataにして保存する。
    genre = genre.replace(r':', r' ')
    with open(f'./Parsed_file/{genre}_{id}.bin', 'wb') as f:
        f.write(stanza.Document.to_serialized(doc))
#-----------------------------------------------------------------------------------------
    print(datetime.datetime.now(), f": Finish {id}")
    print("")