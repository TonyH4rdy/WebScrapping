# Условие :
# Попробуем получать интересующие вакансии на сайте headhunter самыми первыми :)
#
# Необходимо парсить страницу со свежими вакансиями с поиском по "Python" и городами "Москва" и "Санкт-Петербург".
# Эти параметры задаются по ссылке/ Нужно выбрать те вакансии, у которых в описании есть ключевые слова "Django" и "Flask".
# Записать в json информацию о каждой вакансии - ссылка, вилка зп, название компании, город.


from pprint import pprint
import bs4
import fake_headers
import requests
import re
import json

# Генерируем заголовки:
headers = fake_headers.Headers(browser="firefox", os="win")
headers_dict = headers.generate()

# Совершаем запрос:
response = requests.get("https://spb.hh.ru/search/vacancy?text=python+Django&text=python+Flask&area=1&area=2", headers=headers_dict)

main_html_data = response.text
main_html = bs4.BeautifulSoup(main_html_data, "lxml")

# Вытаскиваем требуемые элементы.
# Выделяем все статьи :
vacancy_all = main_html.find('div',  id="a11y-main-content")
# Выделяем список всех объявлений
vacancys_tags =  main_html.find_all('div', class_='vacancy-serp-item__layout')

# Пустой список выходных данных
parsed_data=[]

# Итерируемся по каждому объявлению
for vacancy in vacancys_tags:
    # Найдём заголовок и ссылку.
    # Заголовки и ссылки на статьи находятся внутри тега <h3 ,
    h3_tag = vacancy.find("h3")
    span_tag = h3_tag.find("span")
    a_tag = span_tag.find("a")
    title = a_tag.text  # Добрались до заголовков
    link = a_tag['href'] # Вытащили ссылки
    # Ищем название компании
    company_tag = vacancy.find('div', class_='vacancy-serp-item__meta-info-company')
    company = company_tag.find('a').text

    # Ищем город -vacancy-serp-item__info

    town_teg = list(vacancy.find('div', class_='vacancy-serp-item__info').children)

    # Проверка в Debug-режиме , то бы посмотреть , что скрывается под toun_teg
    print()         # town_teg={list:3} ' [<div class="bloko-v-spacing-container bloko-v-spacing-container_base-2"><div class="bloko-text"><div class="vacancy-serp-item__meta-info-company"><a class="bloko-link bloko-link_kind-tertiary" data-qa="vacancy-serp__vacancy-employer" href="/employer/3529?dpt=3529-3529-prof&amp;hhtmFrom=vacancy_search_list">Сбер для экспертов</a></div><div class="vacancy-serp-item__meta-info-badges"><div class="vacancy-serp-item__meta-info-link"><a class="bloko-link" href="https://feedback.hh.ru/article/details/id/5951" target="_blank"><span class="vacancy-serp-bage-trusted-employer"></span></a></div><div class="vacancy-serp-item__meta-info-link"><a data-qa="vacancy-serp__vacancy_hrbrand vacancy-serp__vacancy_hrbrand_winners" href="http://hrbrand.ru/?utm_source=hh.ru&amp;utm_medium=referral&amp;utm_campaign=icon&amp;utm_term=anonymous" rel="nofollow noindex" target="_blank"><span class="vacancy-serp-bage-hr-brand"></span></a></div><div class="vacancy-serp-item__meta-info-link"><a data-qa="vacancy-serp__vacancy_employer-hh-rating" href="https://rating.hh.ru/history/rating2022?utm_source=hh.ru&amp;utm_medium=referral&amp;utm_campaign=icon&amp;utm_term=anonymous" rel="nofollow noindex" target="_blank"><span class="vacancy-serp-bage-hr-rating"></span></a></div></div></div></div>, <div class="bloko-text" data-qa="vacancy-serp__vacancy-address">Москва</div>, <div class="bloko-v-spacing bloko-v-spacing_base-3"></div>] '
                    # 0=...
                    # 1={Tag}<div class="bloko-text" data-qa="vacancy-serp__vacancy-address">Москва</div>
                    # 2=...
    town = town_teg[1].text

    # Сколько просматривают сейчас
    if vacancy.find('div', class_='online-users--tWT3_ck7eF8Iv5SpZ6WL'):
        count_people = vacancy.find('div', class_='online-users--tWT3_ck7eF8Iv5SpZ6WL').find('span').text
        print(count_people)


    print(title)
    print(link)
    print(company)
    print(town)

    # Вытаскиваем оплату :
    if vacancy.find('span', class_='bloko-header-section-2'):
        salary = vacancy.find('span', class_='bloko-header-section-2').get_text()
    else:
        salary = ''
        print(salary)

    # print()

    # Идём внутрь по ссылке
    response = requests.get(link, headers=headers.generate()).text
    article_html = bs4.BeautifulSoup(response, 'lxml')
    # Находим тег , отвечающий за текст статьи
    # Проводим проверку находится ли текст текущего объявления под тегом "vacancy-description"
    if article_html.find('div', class_='vacancy-description'):
        article_html_tag = article_html.find('div', class_='vacancy-description')
        # И далее, вытаскиваем сам текст:
        article_text = article_html_tag.text
        # Смотрим, что получили
        print(article_text[:140])

    # Найдём c помощью регулярки наличие в тексте требуемых слов - "Django" и "Flask"
        pattern1 = r"Django"
        pattern2 = r"Flask"
        skill_list = re.findall(pattern1, article_text) + re.findall(pattern2, article_text)
        print(len(skill_list), skill_list)
    else:
        article_text = ''
        skill_list = ''

    # Заполняем список выходных данных словарями с требуемыми данными.
    # Данные попадают в выходной список, только если содержимое объявлений отвечает требуемым критериям соответсвия
    # по городу и требуемым навыкам:

    if 'Москва' in town and len(skill_list) > 0 or 'Санкт-Петербург' in town and len(skill_list) > 0:
        parsed_data.append(
        {
         "title": title,
         "link": link,
         "company": company,
         "salary": salary,
         "town": town,
         "len(skill_list)": len(skill_list) # Для проверки
        }
        )
print()
pprint(parsed_data)

# Запись в json

with open("data_file.json", "w", encoding="utf-8") as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=2)