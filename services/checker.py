import json, os
import spacy

import logging
logging.basicConfig(level=logging.DEBUG)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# json_path = os.path.join(BASE_DIR, "config.json")

def config_loader(json_name):
    base = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base, json_name)

    with open(json_path, 'r') as f:
        cfg = json.load(f)

    two_in_a_row_rules = cfg['two_in_a_row']

    quote_type = two_in_a_row_rules['quote_type'] 
    pos_offset = two_in_a_row_rules['pos_offset']
    pos = two_in_a_row_rules['pos']  

    if pos_offset.lower() == 'after':
        pos_offset = 1
    else:
        pos_offset = -1

    return {'quote_type': quote_type, 'pos_offset': pos_offset, 'pos': pos}

class Grammar:

    def __init__(self, config, nlp=None):
        self.config = config
        self.rules = []
        self.nlp = nlp or spacy.load('en_core_web_sm') 

    def get_char_indexes(self, sentence):
        ''' Returns list of characters in string '''
        char_list = []

        for char in sentence:
            char_list.append(char)

        print(char_list)


    def split_into_sentences(self, string_content):
        '''
        Args: raw string content from user
        Returns: list of dicts with sentence text and starting offsets
        '''
        tokenized_content = self.nlp(string_content)
        sentence_list = []

        for sent in tokenized_content.sents:
            sentence_list.append({
                'text': f"{sent}",
                'start': sent.start_char,
                'end': sent.end_char,
            })
        
        return sentence_list

    def tag_sentence(self, sentence, seen):
        doc = self.nlp(sentence)
        doc_tokens = []

        for token in doc:
            if token.is_quote:
                if seen == False:
                    doc_tokens.append({'text': token.text, 
                                       'pos': token.pos_, 
                                       'start_index': token.idx,
                                       'end_index': token.idx,
                                       'quote_type': 'opening_quote',
                                       })
                    seen = True
                else:
                    doc_tokens.append({'text': token.text,
                                       'pos': token.pos_, 
                                       'start_index': token.idx,
                                       'end_index': token.idx,
                                       'quote_type': 'closing_quote',
                                       }),
                    seen = False
            else:
                # if token.whitespace_:
                #     doc_tokens.append({'text': token.whitespace_, 'pos': token.pos_, 'quote_type': None})
                if len(token.text) == 1:
                    doc_tokens.append({'text': token.text, 
                                    'pos': token.pos_, 
                                    'quote_type': None,
                                    'start_index': token.idx, 
                                    'end_index': token.idx})
                else:    
                    doc_tokens.append({'text': token.text, 
                                    'pos': token.pos_, 
                                    'quote_type': None,
                                    'start_index': token.idx, 
                                    'end_index': (token.idx + len(token.text))
                                    })
                
        return (seen, doc_tokens)

    def tag_paragraph(self, paragraph):
        prev_seen = False
        tagged_sentences_list = []

        for sentence in paragraph:
            prev_seen, doc_tokens = self.tag_sentence(sentence, prev_seen)

            tagged_sentences_list.append(doc_tokens)

        return tagged_sentences_list

    def check_quote_and_pos(self, input_string):
        quote_type = self.config['quote_type']
        pos_offset = self.config['pos_offset']
        pos = self.config['pos']

        issues = []

        sentence_list = self.split_into_sentences(input_string)
        sentence_text = [sentence['text'] for sentence in sentence_list]
        tagged_sentences_list = self.tag_paragraph(sentence_text)

        for sentence_index in range(len(tagged_sentences_list)):

            for token_index in range(len(tagged_sentences_list[sentence_index])):
                if tagged_sentences_list[sentence_index][token_index]['quote_type'] == quote_type:

                    if 0 <= token_index + pos_offset < len(tagged_sentences_list[sentence_index]) and token_index + pos_offset*2 < len(tagged_sentences_list[sentence_index]):
                        second_token_index = token_index + pos_offset
                        if tagged_sentences_list[sentence_index][second_token_index]['pos'] == pos:
                            # print('this sentence has the wrong order!')
                            # print(f"'sentence_index': {sentence_index}, 'token': {tagged_sentences_list[sentence_index][token_index]['text']}")
                            # print(f"'sentence_index': {sentence_index}, 'token': {tagged_sentences_list[sentence_index][next_token_index]['text']}")

                            start_index = tagged_sentences_list[sentence_index][token_index]['start_index']
                            end_index = tagged_sentences_list[sentence_index][second_token_index]['end_index']
                            absolute_start = sentence_list[sentence_index]['start'] + start_index
                            absolute_end = sentence_list[sentence_index]['start'] + end_index

                            issues.append({
                                'sentence_index': sentence_index, 
                                'text': tagged_sentences_list[sentence_index][token_index]['text'], 
                                'start_index': start_index, 
                                'end_index': end_index,
                                'absolute_start_index': absolute_start,
                                'absolute_end_index': absolute_end,
                                })

                    else:
                        continue

        return issues    

config = config_loader('config.json')
grammar = Grammar(config)
