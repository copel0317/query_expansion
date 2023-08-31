#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from elasticsearch_dsl import Search, Q


def get_expanded_query_w2v(model, q0, k=3):
    """ 이 함수는 확장된 용어를 반환한다.
    Word2Vec 모델을 사용해서 q0을 비교했을 때,
    이 용어들의 목록을 되돌려 줍니다.
    목록의 각 목록에는 q0의 단어가 포함되어 있습니다.
    그 단어의 가장 비슷한 단어와 함께 말이죠.
    """
    qe = []
    for word in q0.split(' '):
        expanded_words = [pair[0] for pair in model.most_similar(word)[:k]]
        expanded_words.append(word)
        qe.append(expanded_words)
    return qe


def get_expanded_query_glove(model, q0, k=3):
    """ 이 함수는 확장된 용어를 반환한다.
    q0에 비해서 말이죠.
    """
    qe = []
    for word in q0.split(' '):
        expanded_words = [pair[0] for pair in model.most_similar(word,
                                                                 number=k + 1)]
        expanded_words.append(word)
        qe.append(expanded_words)
    return qe


def get_elasticsearch_result(terms, client, index, num_results=10):
    """ Elastic Search에 문의하는 기능
    고객을 이용한 'terms'와 색인화하여 반환하는 용어
    상담을 신청하고 트윗을 달았습니다.
    """
    queries = []
    for term in terms:
        queries.append(Q('match', text=' '.join(term)))
    q = Q('bool', should=queries)
    s = Search(using=client, index=index).query(q)
    result = [(res.text, res.meta.score) for res in s[:1000]]
    return result


def show_most_improved_tweet(original_tweets, expanded_tweets):
    """ 가장 많이 게시된 트윗을 화면별로 보여주는 기능
    Elastic Search의 결과에 올랐습니다. 트윗을 비교해 보세요.
    원래의 트윗과 협의를 확장함으로써 얻은 것입니다.
    """
    most_improved = ('', -1, -1, -1)
    for i, expanded_tweet in enumerate(expanded_tweets):
        for j, original_tweet in enumerate(original_tweets):
            if expanded_tweet == original_tweet and (j - i) > most_improved[1]:
                most_improved = (expanded_tweet, j - i, j, i)
    print("El tweet '{0}' subió {1} posiciones (desde la posicion {2} hasta la posicion {3})".format(*most_improved))


def show_most_devaluated_tweet(original_tweets, expanded_tweets):
    """ 가장 많이 게시된 트윗을 화면별로 보여주는 기능
    Elastic Search 결과에서 하락했습니다. 트윗을 비교해 보세요.
    원래의 트윗과 협의를 확장함으로써 얻은 것입니다.
    """
    most_devaluated = ('', -1, -1, -1)
    for i, expanded_tweet in enumerate(expanded_tweets):
        for j, original_tweet in enumerate(original_tweets[:i]):
            if (expanded_tweet == original_tweet
                    and (i - j)) > most_devaluated[1]:
                most_devaluated = (expanded_tweet, i - j, j, i)
    print("El tweet '{0}' descendió {1} posiciones (desde la posicion {2} hasta la posicion {3})".format(*most_devaluated))
