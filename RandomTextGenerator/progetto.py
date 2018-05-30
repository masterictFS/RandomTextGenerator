import random
import sys

# end of line delimiters.
eol = ['.', '?', '!']


# handles the creation or grammatically accurate random texts
# based on a text received on input.
# @numOfWords says how long the 'predicting key' will be: higher values
# yield texts that make more sense but which have
# less flexibility from the original.
# The algorithm uses an elementary Markov Chain to determine which words
# are more likely to follow one another.
class MarkovGenerator(object):
    def __init__(self, inputText, numOfWords=2):
        super(MarkovGenerator, self).__init__()
        self.inputText = inputText
        self.numOfWords = numOfWords
        # arbitrary limit for operations subjected to timeout.
        # could use some tweaking.
        self.maxTimeOutTries = len(self.inputText) * 10

    # builds the dictionary to generate the random text.
    def _buildDict(self):
        self.d = {}
        key = []
        for i in range(self.numOfWords):
            key.append(None)
        key = tuple(key)

        for word in self.inputText:
            if key not in self.d:
                self.d[key] = []
            self.d[key].append(word)

            keyArr = []
            for i in range(0, self.numOfWords - 1):
                keyArr.append(key[i + 1])
            keyArr.append(word)
            key = tuple(keyArr)

        if key not in self.d:
            self.d[key] = []
        self.d[key].append(None)

    # generates the text and returns it as a string.
    # if the dictionary hasn't been generated before
    # it's built on the first execution and reused later.
    # the first word is always one starting with a capital letter (if found).
    # @maxLen tells the minimum length (in words) of the generated texts.
    # when that value is exceeded generation goes on until an eol character
    # is found (or a timeout is reached).
    def generateText(self, maxLen):
        try:
            self.d
        except AttributeError:
            self._buildDict()
        key = []
        res = []
        count = 0
        key = random.choice(list(self.d))
        word = self.d[key][0]

        timeOutCount = 0
        while not word[0].isupper() and timeOutCount < self.maxTimeOutTries:
            key = random.choice(list(self.d))
            word = self.d[key][0]
            timeOutCount += 1

        while word and count < self.maxTimeOutTries:
            res.append(word)

            if (count < maxLen or word[-1] not in eol):
                keyArr = []
                for i in range(0, self.numOfWords - 1):
                    keyArr.append(key[i + 1])
                keyArr.append(word)
                key = tuple(keyArr)

                word = random.choice(self.d[key])
                count += 1
            else:
                break

        res = ' '.join(res)
        if res[-1] not in eol:
            res += '.'

        return res


# reads a text fields and yields an array of its words.
# newlines are preserverd, but consecutive ones (after the first).
# are eliminated.
# @encoding explicitly specifies the encoding type
def readInput(fileName, encoding):
    ret = []
    try:
        infile = (
            open(fileName, encoding=encoding)
            if encoding
            else open(fileName))

        lines = infile.readlines()
        infile.close()

        for line in lines:
            for word in line.split():
                ret.append(word)
            ret.append('\n')
    except FileNotFoundError:
        print("Invalid filename: '" + fileName + "'")
    return removeRepeatedNewLine(ret)


# removes repeating newline characters from an array of words
# newlines are treated as independent words.
def removeRepeatedNewLine(text):
    text = [
        y[1] for y in enumerate(text) if (
            y[0] + 1 < len(text) and text[y[0]] != text[y[0] + 1]
        ) or y[0] == len(text) - 1
    ]
    return text


# saves @text to @name.txt
def saveText(name, text):
    name = 'default' if len(name) == 0 else name
    # strips double file extension
    name = name[:-4] if name[-4:] == '.txt' else name
    txtfile = open(name + '.txt', 'w')
    txtfile.write(text)
    txtfile.close()
    print('saved to: ' + name + '.txt')


# main program execution, prints the generated text to output.
# prompts user for antoher one and/or saving the output to file
# the expected arguments are:
# @fileName
# @maxLen: defaults to 100
# @numOfWords: defaults to 2
# @encoding: explicitly specifies the encoding of the input
# might be useful if execution fails due to encoding errors
def main():
    try:
        fileName = sys.argv[1]
    except IndexError:
        print('No filename provided.')
        return
    try:
        maxLen = int(sys.argv[2])
    except (IndexError, TypeError, ValueError) as e:
        maxLen = 100
    try:
        numOfWords = int(sys.argv[3])
    except (IndexError, TypeError, ValueError) as e:
        numOfWords = 2
    try:
        encoding = sys.argv[4]
    except (IndexError, TypeError, ValueError) as e:
        encoding = ''
    g = MarkovGenerator(readInput(fileName, encoding), numOfWords)

    saved = False
    while True:
        if not saved:
            t = g.generateText(maxLen)
            print('\n' + t)
        print()

        inputPrompt = 'Another one (y/n)?'
        if not saved:
            inputPrompt += ' or save (s)?'
        inputPrompt += '\n'

        decision = input(inputPrompt)
        print()

        if (not saved) and len(decision) != 0 and decision[0].lower() == 's':
            name = input('input name of file:\n')
            saveText(name, t)
            saved = True
            continue

        saved = False
        if not (len(decision) == 0 or decision[0].lower() == 'y'):
            break


if __name__ == '__main__':
    main()
