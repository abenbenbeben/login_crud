import wikipedia

def wiki(word):
    wikipedia.set_lang('ja')
    candidate_list = wikipedia.search(word)
    if not candidate_list:
        result = '該当する結果がありませんでした'
    else:
        search_page = wikipedia.page(candidate_list[0])
        result = search_page.summary
        
    return result

if __name__ == '__main__':
    print(wiki('きめつの刃'))