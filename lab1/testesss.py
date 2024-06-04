from bs4 import BeautifulSoup
import requests
import json
from urllib.parse import urljoin

SITE_URL = 'https://lenta.ru'
PARTS_URL = f'{SITE_URL}/parts/news'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

# Функция для получения списка URL статей на странице
def get_article_urls(page_url):
    response = requests.get(page_url, headers=headers)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find_all(class_='parts-page__item')
        return [item.find('a').get('href') for item in body if item.find('a')]
    else:
        print('Ошибка при запросе:', response.status_code)
        return []

# Функция для получения содержания статьи
def get_article_content(article_url):
    response = requests.get(article_url, headers=headers)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1').text if soup.find('h1') else 'No Title'
        body = [p.text for p in soup.find('body').find_all('p')]
        category_tag = soup.find('a', class_='topic-header__rubric')
        category = category_tag.text if category_tag else 'Неизвестно'
        date_tag = soup.find('time', class_='topic-header__time')
        create_date = date_tag.get('datetime') if date_tag else 'Неизвестно'
        
        return title, category, create_date, body, article_url
    else:
        print('Ошибка при запросе:', response.status_code)
        return None, None, None, None, None

# Функция для сохранения данных в JSON файл
def save_to_json(data_list):
    with open('articles.json', 'w', encoding='utf-8') as file:
        json.dump(data_list, file, ensure_ascii=False, indent=4)

# Основная функция для запуска парсинга и сохранения данных
def main():
    data_list = []  # Список для хранения данных статей
    page_urls = [PARTS_URL]  # начальная страница
    article_urls = get_article_urls(PARTS_URL)  # получаем адреса статей на начальной странице
    for article_url in article_urls:
        full_article_url = urljoin(SITE_URL, article_url)
        title, category, create_date, body, url = get_article_content(full_article_url)  # получаем содержание статьи
        if title and body and category and create_date:
            data = {
                "title": title,
                "category": category,
                "create_date": create_date,
                "body": body,
                "url": full_article_url
            }
            data_list.append(data)  # Добавляем данные статьи в список
    save_to_json(data_list)  # Сохраняем все данные в файл

if __name__ == "__main__":
    main()
