import os
import json
from flask import Flask, request, Response
from chat import Chat

nickname = 'kirillkuzin'
host = '127.0.0.1'
port = os.environ.get('CHAT_PORT')
node = host + ':' + port

application = Flask(__name__)
ch = Chat(node)

@application.route('/dialogs/<int:dialogIndex>/nodes', methods=['POST'])
def addNode(dialogIndex):
    requestData = request.get_json()
    node = requestData['nodeAddress']
    nodeDialogIndex = requestData['nodeDialogIndex']
    status = ch.addNode(dialogIndex, node, nodeDialogIndex)
    if status:
        return response('', 201)

@application.route('/dialogs', methods=['GET'])
def getDialogs():
    data = ch.dialogs
    return response(data, 200)

@application.route('/dialogs/<int:dialogIndex>', methods=['GET'])
def getDialog(dialogIndex):
    data = ch.dialog(dialogIndex)
    return response(data, 200)

@application.route('/dialogs', methods=['POST'])
def newDialog():
    data = ch.newDialog(nickname, node, 'Initial message')
    return response(data, 201)

@application.route('/dialogs/<int:dialogIndex>/messages', methods=['POST'])
def sendMessage(dialogIndex):
    requestData = request.get_json()
    messageText = requestData['messageText']
    data = ch.sendMessage(dialogIndex, nickname, messageText)
    if data:
        return '', 200

def response(data, statusCode, error=None, errorCode=None):
    responseData = json.dumps({
        'data': data,
        'erros': [{}],
    })
    return Response(
        responseData,
        status=statusCode,
        mimetype='application/json'
    )

if __name__ == '__main__':
    application.run(
        debug=True,
        host=host,
        port=int(port)
    )
