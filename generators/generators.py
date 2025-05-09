import random as r

def random_emotion():
    emotions = ['neutral', 'happy', 'sad', 'angry', 'fear', 'surprise'] # Без отвращения(
    return r.choice(emotions)

def emote_to_text(emote):
    emotions = {
        'neutral': 'Нейтрально',
        'happy' : 'Веселье',
        'sad' : 'Грусть',
        'angry' : 'Злость',
        'fear' : 'Ужас',
        'surprise' : 'Удивление'
    }
    return emotions[emote]