import docx

class quiz:
    def __init__(self,host,num):
        self.host = host
        self.totalQuestions = int(num)
        self.players = dict()
        self.playerNum = 0
        self.curQuestion = -1
        self.responses = [[None for i in range(self.totalQuestions)] for j in range(20)]
        self.pounceOpen = False
        self.questions = []

    def pounce(self,name,response):
        if self.curQuestion <= self.totalQuestions:
            val = int(self.players[name]) - 1
            self.responses[val][self.curQuestion] = response

    def nextQuestion(self):
        self.curQuestion += 1

    def join(self,name):
        self.playerNum += 1
        self.players[name] = self.playerNum
        if self.playerNum >= 20 :
            self.responses.append([None for i in range(self.totalQuestions)])

    def generateQues(self,filename,delimiter=''):
        doc = docx.Document(filename)
        temp = ''
        for para in doc.paragraphs:
            if para.text == str(delimiter):
                self.questions.append(temp)
                temp = ''
            else:
                temp+=para.text + "\n\n"
        return '\n\n'.join(self.questions)