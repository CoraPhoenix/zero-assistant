import random
import numpy as np
import pickle as pkl
import nltk
from nltk.stem import WordNetLemmatizer
lemmatiser = WordNetLemmatizer()

words = pkl.load(open('data\words.pkl', 'rb'))
classes = pkl.load(open('data\classes.pkl', 'rb'))


def clear_writing(writing):
    """
        Clear inputted sentences
    """

    # tokenises all inserted sentences, and lemmatises each one of them
    sentence_words = nltk.word_tokenize(writing)
    return [lemmatiser.lemmatize(word.lower()) for word in sentence_words]


# retorna 0 ou 1 para cada palavra da bolsa de palavras


def bag_of_words(writing, words):
    """
        Get cleared sentences and generates a bag of words which will be used to predict classes based on training results
    """
    # tokenise the pattern
    sentence_words = clear_writing(writing)

    # generate a N word matrix
    word_bag = [0]*len(words)
    for sentence in sentence_words:
        for i, word in enumerate(words):
            if word == sentence:
                # assign 1 to word bag if current word is in the sentence position
                word_bag[i] = 1

    return(np.array(word_bag))


def predict_class(writing, model):
    """
      Predict from bag of words, using error limit of 0.25 to avoid overfitting, and classify results by probability
    """

    # filter out predictions below 0.25
    prediction = bag_of_words(writing, words)
    response_prediction = model.predict(np.array([prediction]))[0]
    results = [[index, response] for index, response in enumerate(response_prediction) if response > 0.25]    

    # verifies if there's no 1 in the list; if that's the case, send default response (anything_else) 
    if "1" not in str(prediction) or len(results) == 0 :
        results = [[0, response_prediction[0]]]

    # classifies by probability
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]


def get_response(intents, data):
    """
		Gets the generated list and verifies data file to produce the outputs with highest probability
    """
    tag = intents[0]['intent']
    list_of_intents = data['intents']
    for idx in list_of_intents:
        if idx['tag'] == tag:
            # gets a random answer if selected tag contains more than one option of answer
            result = random.choice(idx['responses'])
            break

    return result