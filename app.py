from flask import Flask, render_template, request, send_file
from forms import TextForm
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

app.config['SECRET_KEY'] = 'bf41cdb8be7df3e599e80a7e747bb926'

@app.route("/", methods=['POST', 'GET'])
def add_Text():

    form = TextForm()
    text = request.form.get("text", "")

    with open('download.txt', 'w', encoding='utf-8') as fo:
        fo.write(text)

    files = {
        'data':open("download.txt",'rb'),
    }

    apiURL = "http://lindat.mff.cuni.cz/services/nametag/api/recognize"
    response = requests.post(apiURL,files = files)
    NametagResponse = response.json()

    textData = (str(NametagResponse))
    clearedText = delete(textData)
    replacedText = replace(clearedText)

    with open('downloadText.txt', 'w', encoding='utf-8') as fo:
        fo.write(replacedText)

    return render_template("home.html", form=form, text=replacedText)

@app.route('/upload', methods = ['POST', 'GET'])  
def upload():  

    if request.method == 'POST':  
        f = request.files['file']
        f.save(f.filename)  
        global name
        name = f.filename

    checkValues = (request.form.getlist('checkbox'))
    uploadfile = open(name, "r", encoding='utf-8')
    soup = BeautifulSoup(uploadfile, features = "html.parser")
    values = soup.find_all(checkValues)
    dataToSend = ""
    for heading in values:
        dataToSend = dataToSend + heading.text.strip() + ";"
    
    with open('dataFile.txt', 'w', encoding='utf-8') as fo:
        fo.write(dataToSend)

    files = {
        'data':open("dataFile.txt",'rb'),
    }

    apiURL = "http://lindat.mff.cuni.cz/services/nametag/api/recognize"
    response = requests.post(apiURL,files = files)
    NametagResponse = response.text

    clearedText = delete(NametagResponse)
    replacedText = replace(clearedText)

    responseList = list(replacedText.split(';'))
    responseList.pop()

    for i, value in enumerate(values):
        value.string.replace_with(responseList[i])

    with open('modified.html', 'w', encoding='utf-8') as fo:
        fo.write(soup.prettify(formatter=None))

    return render_template("potvrdenie.html", nazov = name)

def delete(deletetext):

    before = deletetext.partition("<sentence>") 
    deletetext = deletetext.replace(before[0],"")
    deletetext = re.sub(r'<sentence>|</sentence>|<token>|</token>',"",deletetext)
    deletetext = deletetext.replace("\\", "").replace("[", "").replace("]", "").replace("'", "").replace("}", "")
    return deletetext

def replace(replacetext):

    replacetext = replacetext.replace('<ne type="P">','<span itemscope itemtype="http://schema.org/Person">')
    replacetext = replacetext.replace('<ne type="A">','<span itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">')
    replacetext = replacetext.replace('<ne type="pf">','<span itemprop="firstName">')
    replacetext = replacetext.replace('<ne type="gs">','<span itemprop="street">')
    replacetext = replacetext.replace('<ne type="ah">','<span itemprop="streetNumber">')
    replacetext = replacetext.replace('<ne type="if">','<span itemprop="company">')
    replacetext = replacetext.replace('<ne type="ps">','<span itemprop="lastName">')
    replacetext = replacetext.replace('<ne type="gu">','<span itemprop="city">')
    replacetext = replacetext.replace('</ne></ne>','</span> </span>')
    replacetext = replacetext.replace('</ne>','</span>')

    return replacetext

@app.route('/downloadtext')  
def downloadtext():

    return send_file("downloadText.txt", as_attachment=True)

@app.route('/download')  
def download():

    return send_file("modified.html", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

