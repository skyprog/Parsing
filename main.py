import json
import requests
from bs4 import BeautifulSoup
import os
import time
from random import randrange

# *Ключевые слова вводить через запятую в параметре функции get_urls (в самом низу)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}

def get_urls(key_words):

    list_key_words = key_words.split(',')
    
    count = 1
    books_urls = []

    while True:
        if len(list_key_words) == 1:   
            url = f"https://ua1lib.org/s/{list_key_words[0]}?page={count}"

        elif len(list_key_words) > 1:
            str_key_words = ''
            for i in list_key_words:
                str_key_words += '%20' + i.strip()
            url = f"https://ua1lib.org/s/{str_key_words}?page={count}"    

        page = requests.get(url, headers=headers)
        result = page.content
        soup = BeautifulSoup(result, 'lxml')

        book_links = soup.find_all('a', attrs={'style':'text-decoration: underline;'})

        for product in book_links:
            book = 'https://ua1lib.org' + product.get('href')
            books_urls.append(book)

        print('Страница ',count)
        
        count += 1
        
        time.sleep(randrange(2,3))

# кол-во страниц для парсинга, сайт выдает 10
        if count == 11:
            break
    
    with open('Parsing_ua1lib.org/books_url_list.txt', 'w') as file:
        for line in books_urls:
            file.write(f'{line}\n')

    print('Ссылки собраны!')

def get_data():
    
    with open('Parsing_ua1lib.org/books_url_list.txt') as file:

        lines = [line.strip() for line in file.readlines()]
        data_dict = []
        data_img = []
        
        print('Происходит парсинг книг по ссылкам...')

# Поставил срез в 50 книг
        for line in lines[0:51]:
            url = requests.get(line)
            result = url.content

            soup = BeautifulSoup(result, 'lxml')

            try:
                book_name = soup.find('h1', itemprop="name").text.strip()
            except Exception:
                print("'Error: NoneType object has no attribute 'text'")
                continue    

            try:
                book_author = soup.find('a', itemprop="author").text.strip()
            except Exception:
                print("'Error: NoneType object has no attribute 'text'")
                continue  

            try:
                book_descpiption = soup.find('div', id="bookDescriptionBox").text.strip()
            except Exception:
                book_descpiption = 'Нет описания'

            try:    
                book_pages = soup.find('div', class_='bookProperty property_pages').find('div', class_='property_value').find('span').text.strip()
            except Exception:
                book_pages = 'Нет описания'

            try:        
                book_year = soup.find('div', class_="bookProperty property_year").text.strip().split()
                if int(book_year[-1]):
                    year = book_year[-1]
            except Exception:
                year = '_'
            try:
                book_language = soup.find('div', class_="bookProperty property_language").text.strip().split()
            except Exception as ex_lang:
                print(ex_lang)
                book_language = '_'

            book_image = soup.find('div', class_="details-book-cover-content").find('a').get('href')
            data_img.append(book_image)

            book_rating = soup.find('div', class_="book-rating").text.strip().split()
            book_rating_out = ''.join(book_rating) 
            
            data = {
                'Название': book_name,
                'Автор': book_author,
                'Описание': book_descpiption,
                'Страниц': book_pages,
                'Год': year,
                'Язык': book_language[-1],
                'Рейтинг': book_rating_out,
                'Картинка': book_image,
                'Ссылка на книгу': line
            }
            
            data_dict.append(data)

            with open('Parsing_ua1lib.org/data.json', 'w', encoding="utf-8") as json_file:
                json.dump(data_dict, json_file, indent=4, ensure_ascii=False)

            print('Книга: ',len(data_dict))

# Без рандомной паузы между запросов выдает ошибку NoneType object has no attribute 'text' 
# и каждый раз на разных ссылках, хотя все ок с этими ссылкам, наверное сайт блокирует много запросов подряд       
            time.sleep(randrange(1,2))     

        print('Книги спарсились!')


def download_imgs(file_path):

    try:
        with open(file_path) as file:
            src = json.load(file)
    except Exception as ex:
        print(ex)

    print("Скачивание обложек книг в папку 'data'...")

    for item in src:
        item_name = item.get("Название")
        item_imgs = item.get("Картинка")

        print(item_imgs)

        if not os.path.exists(f"Parsing_ua1lib.org/data/{item_name[0:55]}"):
            os.mkdir(f"Parsing_ua1lib.org/data/{item_name[0:55]}")

        try:    
            r = requests.get(url=item_imgs)
            with open(f"Parsing_ua1lib.org/data/{item_name[0:55]}/{item_name[0:55]}.jpg", "wb") as file:
                file.write(r.content)

        except Exception as ex_url:
            print('No cover', ex_url)
            continue        

    print('Обложки книг получены!')       

def main():
    get_urls('Python,JavaScript,Docker')
    get_data()
    download_imgs("Parsing_ua1lib.org/data.json")

if __name__ == '__main__':
    main()
