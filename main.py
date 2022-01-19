from PyQt5.QtWidgets import QMainWindow , QApplication, QLabel, QTextEdit, QPushButton, QListWidget
from PyQt5 import uic
import sys
import moviepy.editor as mp
import os
from google.cloud import speech
from hatesonar import Sonar
from pathlib import Path

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'CREDENTIALS'


class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()
        #Load the ui file
        uic.loadUi('ui.ui', self)
        #Define widgets
        self.textLable= self.findChild(QLabel,"textLable")
        #self.lable4= self.findChild(QLabel,"lable_4")
        self.lexiconLable= self.findChild(QLabel,"lexiconLable")
        self.hateWordsCountLable= self.findChild(QLabel,"hateWordsCountLable")
        self.textedit=self.findChild(QTextEdit,"textEdit")
        self.button=self.findChild(QPushButton,"pushButton")

        self.privateLexiconListView = self.findChild(QListWidget,"privateLexiconListView")
        self.addToLexiconBt=self.findChild(QPushButton,"addToLexiconBt")
        self.removeFromLexiconBt=self.findChild(QPushButton,"removeFromLexiconBt")
        self.lexiconText=self.findChild(QTextEdit,"lexiconText")
        self.detectionLable = self.findChild(QLabel,"detectionLable")
        #Do something
        self.button.clicked.connect(self.btAnalayze)
        self.addToLexiconBt.clicked.connect(self.addToLexicon)
        self.removeFromLexiconBt.clicked.connect(self.removeFromLexicon)
        #Show The App
        self.show()
    def btAnalayze(self):
        mp4_path = self.textEdit.toPlainText()                                          #get mp4 path
        self.detectionLable.setText("Convert to a audio file")
        mp3_path = VideoToMp3(mp4_path)                                                 #create mp3 file and get his path
        if(mp3_path!="null"):
            self.detectionLable.setText("Convert from speech to text")
            text = SpeechToText(mp3_path)                                               #get the text from the mp3 file
            userLexicon = GetLexiconFromListView(self.privateLexiconListView)           #read the user lexicon from QListWidget
            hateWordsInText = HateKeyWordDetector(text, userLexicon)                    #count how many words from the text are in the lexicon
            self.detectionLable.setText("Predict the detection")
            class_name = hateSonarCheck(text)                                           #check if the text is good or bad
            #set lables
            self.lexiconLable.setText(str(hateWordsInText))
            self.hateWordsCountLable.setText(str(len(hateWordsInText)))
            self.detectionLable.setText(str((class_name)))
        else:
            self.detectionLable.setText("Wrong video path")
    def addToLexicon(self):
        self.privateLexiconListView.addItem(self.lexiconText.toPlainText())
    def removeFromLexicon(self):
        for item in self.privateLexiconListView.selectedItems():
            self.privateLexiconListView.takeItem(self.privateLexiconListView.row(item))
#input: mp4 path, convert to mp3 and save in the same path. output: mp3 path
def VideoToMp3(path):
    if(os.path.isfile(path)):
        clip = mp.VideoFileClip(path)
        mp3_path = os.path.splitext(os.path.basename(path))[0]+'.mp3'
        clip.audio.write_audiofile(mp3_path)
        return mp3_path
    else:
        return "null"
#input mp3 path, output: text
def SpeechToText(path):
    print("SpeechToText()")
    speech_client = speech.SpeechClient()
    with open(path, 'rb') as f1:
        byte_data_mp3 = f1.read()
    audio_mp3 = speech.RecognitionAudio(content=byte_data_mp3)
    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=0,
        max_speaker_count=10,
    )
    config_mp3 = speech.RecognitionConfig(
        sample_rate_hertz=48000,
        enable_automatic_punctuation=True,
        language_code='en-US',
        #audio_channel_count=2,
        model='video',
        diarization_config=diarization_config

    )
    respone_standart_mp3 = speech_client.recognize(
        config=config_mp3,
        audio=audio_mp3
    )
    print("SpeechToText()",respone_standart_mp3)
    output=""
    for res in respone_standart_mp3.results:
        try:
            output = output+ res.alternatives[0].transcript
        except:
            output = output+""
    return output
##input List view, output list
def GetLexiconFromListView(privateLexiconListView):
    items = []
    for x in range(privateLexiconListView.count()):
        items.append(privateLexiconListView.item(x).text())
    return items
#Get text and list and count how many words are in the list
def HateKeyWordDetector(text,lexicon):
    textList = text.split()
    hateWordsInText = []
    count = 0
    for x in textList:  # checking the array over the text
        if x in lexicon:  # counter to know how many aggressive words are in the text
            print(x)
            count += 1
            hateWordsInText.append(x)
    return hateWordsInText
#input text, output Hate sppech or not by hatesonar
def hateSonarCheck(text):
    sonar = Sonar()
    className =sonar.ping(text=text)['top_class']
    print(sonar.ping(text=text))
    if(className=='neither'):
        return "No hate speech was detected"
    else:
        return "Hate speech was detected"

app = QApplication(sys.argv)
UIWindow =UI()
app.exec_()