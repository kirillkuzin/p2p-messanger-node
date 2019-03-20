import requests
import time
import hashlib
from threading import Thread

class Chat():

    def __init__(self, nodeAddress):
        self.nodeAddress = nodeAddress
        self.dialogs = []

    def dialog(self, dialogIndex):
        return {dialogIndex: self.dialogs[dialogIndex]}

    def newDialog(self, owner, node, initialMessage=None):
        self.dialogs.append({
            'participants': [owner],
            'messages': [],
            'nodes': [
                {
                    'address': node,
                    'dialogIndex': len(self.dialogs)
                },
            ],
        })
        dialogIndex = len(self.dialogs) - 1
        if initialMessage:
            self.sendMessage(dialogIndex, None, 'Initial message.')
        syncThread = Thread(target=self.syncNode, args=(dialogIndex,), daemon=True)
        syncThread.start()
        return {dialogIndex: self.dialogs[dialogIndex]}

    def sendMessage(self, dialogIndex, sender, messageText):
        messageTime = time.time()
        hashString = str(sender) + ' ' + messageText + ' ' + str(len(self.dialogs[dialogIndex]['messages'])) + ' ' + str(messageTime)
        hash = hashlib.sha256(hashString.encode('utf-8'))
        self.dialogs[dialogIndex]['messages'].append({
            'sender': sender,
            'message': messageText,
            'time': messageTime,
            'hash': hash.hexdigest()
        })
        return True

    def addNode(self, dialogIndex, node, nodeDialogIndex):
        self.dialogs[dialogIndex]['nodes'].append({
            'address': node,
            'dialogIndex': nodeDialogIndex,
        })
        return True

    def connectToNode(self, node, nodeDialogIndex):
        # dialogIndex = newDialog('kirill', 'node')
        requests.put('http://' + node + 'nodes/{}'.format(nodeDialogIndex))

    def syncNode(self, dialogIndex):
        while True:
            for node in self.dialogs[dialogIndex]['nodes']:
                address = node['address']
                if address != self.nodeAddress:
                    nodeDialogIndex = node['dialogIndex']
                    nodeDialog = requests.get('http://' + address + '/dialogs/{}'.format(nodeDialogIndex)).json()
                    nodeDialog = nodeDialog['data'][str(nodeDialogIndex)]
                    nodeMessages = nodeDialog['messages']
                    messages = list(self.dialogs[dialogIndex]['messages'])
                    for nodeMessage in nodeMessages:
                        messageExist = False
                        for message in messages:
                            if nodeMessage['hash'] == message['hash']:
                                messageExist = True
                                break
                        if not messageExist:
                            self.dialogs[dialogIndex]['messages'].append(nodeMessage)
                            print(self.dialogs[dialogIndex])
