'''
 Letter Game Backend
 Dan Medani 2017
'''

from __future__ import print_function

import boto3
import json

print('Loading function')

def respond(err, res=None):
    print('res', res)
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

'''
Is a string numeric?
'''
def isNumeric(st):
    try:
        v = int(st)
    except ValueError:
        return False
    return True

'''
Format a puzzle for the user.
'''
def formatPuzzle(puzz, k):
    phrase = puzz['phrase']
    guessWord = puzz['guessWord']

    puzzle = []
    for i in xrange(len(phrase)):
        if guessWord[i]:
            puzzle.insert(len(puzzle), phrase[i][0:1])
        else:
            puzzle.insert(len(puzzle), phrase[i])

    return ' '.join(puzzle)

'''
Grab user's next puzzle, format and return.
'''
def getNextPuzzle(user_id):
    users = boto3.resource('dynamodb').Table('lettergame_users')
    user = users.get_item(Key={'id': user_id})

    if user == None:
        return respond({'message': 'User ' + user_id + ' not found.'}, None)

    nextPuzzleId = user['Item']['nextPuzzleId']

    if nextPuzzleId == None:
        return respond(None, {'message': 'You Win.'})

    phrases = boto3.resource('dynamodb').Table('lettergame_phrases')
    nextPuzzle = phrases.get_item(Key={'id': nextPuzzleId})

    if nextPuzzle == None:
        return respond({'message': 'Puzzle ' + nextPuzzleId + ' not found.'}, None)

    return respond(None, formatPuzzle(nextPuzzle['Item'], 1))

'''
Main event handler for lambda.
'''
def lambda_handler(event, context):
    operations = {
        # 'DELETE': lambda phrases, x: phrases.delete_item(**x),
        'GET': lambda phrases, x: phrases.scan(**x)
        # 'POST': lambda phrases, x: phrases.put_item(**x),
        # 'PUT': lambda phrases, x: phrases.update_item(**x),
    }

    operation = event['context']['http-method']
    if operation in operations:
        if operation == 'GET':
            user_id = event['params']['querystring']['u']
            return getNextPuzzle(user_id)
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
