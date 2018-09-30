import json
import nltk
import string
from nltk.corpus import stopwords
import editdistance

# устанавливаем коэффициенты модели
kO = 0.5  # доля объекта в итоговом весе фразы
kA = 0.3  # доля действия в итоговом весе фразы
kF = 0.2  # доля общего соответствия фразы


# основной метод
def main(source):
    # загружаем объекты
    with open("objects.json", encoding='utf-8') as f:
        objects = json.load(f)
    # загружаем действия
    with open("actions.json", encoding='utf-8') as f:
        actions = json.load(f)
    # загружаем целевые фразы
    with open("targets.json", encoding='utf-8') as f:
        targets = json.load(f)
    # класс для результирующего массива
    class Result:
        def __init__(self, id=None, operation=None, score=None):
            self.id = id
            self.operation = operation
            self.score = score

    resultList = []

    # метод добавления элекментов в результирующий массив
    def addResultByObject(object_id, action_id, target_id, score):
        for target in targets['targets']:
            if (target['object'] == object_id) or (target['action'] == action_id) or (target['id'] == target_id):
                found = 'N'
                for item in resultList:
                    if item.id == target['id']:
                        existItem = item
                        found = 'Y'
                if found == 'Y':
                    existItem.score = existItem.score + score
                else:
                    resultList.append(Result(target['id'], target['operation'], score))

    # 1. предварительная очистка введенной фразы и токенизация
    source = source.lower();
    intab = "acekopxyABCEHKMOPT0Ё"
    outtab = "асекорхуАВСЕНКМОРТое"
    trantab = str.maketrans(intab, outtab)
    source = source.translate(trantab)
    source_tokens = tokenize_me(source)

    # 2. Ищем объекты
    for token in source_tokens:
        for object in objects['objects']:
            for synonym in object['synonyms']:
                distance = editdistance.eval(token, synonym['word'])
                if distance <= int(synonym['l']):
                    addResultByObject(object['id'], '', '',
                                      kO * float(synonym['score']) * (len(token) - distance) / len(token))

    # 3. Ищем действия
    for token in source_tokens:
        for action in actions['actions']:
            for synonym in action['synonyms']:
                distance = editdistance.eval(token, synonym['word'])
                if distance <= int(synonym['l']):
                    addResultByObject('', action['id'], '',
                                      kA * float(synonym['score']) * (len(token) - distance) / len(token))

    # 4. сравниваем всю фразу
    for token in source_tokens:
        for target in targets['targets']:
            target_tokens = tokenize_me(target['operation'])
            score = 0
            for i in range(len(target_tokens)):
                distance = editdistance.eval(token, target_tokens[i])
                if distance <= 4:
                    # Считаем, что данное слово из введенной фразы совпало с одним из слов искомой фразы. Повышаем оценку данной фразы пропорционально длине слова
                    score = score + len(target_tokens[i])/len(target['operation'])*(len(token) - distance)/len(token)
            addResultByObject('', '', target['id'], kF*score)

    # 5. Формируем итоговый массив элементов
    resultList = sorted(resultList, key=lambda x: x.score, reverse=True)
    resultList = resultList[:5]
    resultList = [value for value in resultList if value.score > 0.1]
    if len(resultList) == 0:
        addResultByObject('', '', '0', 1);

    json_string = json.dumps([ob.__dict__ for ob in resultList])
    return json_string


def tokenize_me(file_text):
    # firstly let's apply nltk tokenization
    tokens = nltk.word_tokenize(file_text)

    # let's delete punctuation symbols
    tokens = [i for i in tokens if (i not in string.punctuation)]

    # deleting stop_words
    stop_words = stopwords.words('russian')
    stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])
    tokens = [i for i in tokens if (i not in stop_words)]

    # cleaning words
    tokens = [i.replace("«", "").replace("»", "") for i in tokens]

    return tokens
