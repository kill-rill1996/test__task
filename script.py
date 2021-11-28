import urllib.request
import xml.dom.minidom as minidom
import datetime
import sys
import argparse


def get_data(url_params):
    url_path = f'https://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={url_params}'
    file = urllib.request.urlopen(url_path)
    return file.read()


def get_currency_value(xml_data):
    dom = minidom.parseString(xml_data)
    dom.normalize()

    elements = dom.getElementsByTagName("Valute")
    currency_dict = {}

    for node in elements:
        for child in node.childNodes:
            if child.nodeType == 1:
                if child.tagName == "Value":
                    if child.firstChild.nodeType == 3:
                        value = float(child.firstChild.data.replace(',', '.'))
                if child.tagName == "CharCode":
                    if child.firstChild.nodeType == 3:
                        char_code = child.firstChild.data
            try:
                currency_dict[char_code] = value
            except:
                pass
    return currency_dict


def get_currency_dict(start, end):
    valute_dict = {}

    while start <= end:
        date_str = end.strftime("%d/%m/%Y")
        xml_data = get_data(date_str)
        valute_dict[date_str] = get_currency_value(xml_data=xml_data)
        end -= datetime.timedelta(days=1)

    return valute_dict


def average_rub_course(valute_dict):
    res_dict = {}
    for key in valute_dict.keys():
        for valute in valute_dict[key].keys():
            if not valute in res_dict.keys():
                res_dict[valute] = []
            else:
                res_dict[valute].append(valute_dict[key][valute])
    for key in res_dict.keys():
        res_dict[key] = float('{:.4f}'.format(sum(res_dict[key]) / len(res_dict[key])))
    return res_dict


def max_valutes_value(valute_dict):
    res_dict = {}
    for key in valute_dict.keys():
        for valute in valute_dict[key].keys():
            if not valute in res_dict.keys():
                res_dict[valute] = {'date': key, 'price': valute_dict[key][valute]}
            else:
                if res_dict[valute]['price'] < valute_dict[key][valute]:
                    res_dict[valute] = {'date': key, 'price': valute_dict[key][valute]}
    return res_dict


def min_valutes_value(valuet_dict):
    res_dict = {}
    for key in valuet_dict.keys():
        for valute in valuet_dict[key].keys():
            if not valute in res_dict.keys():
                res_dict[valute] = {'date': key, 'price': valuet_dict[key][valute]}
            else:
                if res_dict[valute]['price'] > valuet_dict[key][valute]:
                    res_dict[valute] = {'date': key, 'price': valuet_dict[key][valute]}
    return res_dict


def print_result(res_dict, print_type=None):
    for key in res_dict.keys():
        if print_type in ['Min', 'Max']:
            print(f'{print_type} value of the {key} was at {res_dict[key]["date"]} - {res_dict[key]["price"]} rub')
        else:
            print(f'Average value of {key} - {res_dict[key]}')


def main(start, end):

    # Веедены обе даты либо ни одна (оба значения - None)
    if (start and end) or not (start and end):
        if start:
            try:
                date_time_start = datetime.datetime.strptime(start, "%d.%m.%Y")
                date_time_end = datetime.datetime.strptime(end, "%d.%m.%Y")
            except ValueError:
                raise ValueError('Неправильный формат введенных данных (необходимый формат - день.месяц.год)')

            # Обработка еще не наступивших дат
            if date_time_start > datetime.datetime.now() or date_time_end > datetime.datetime.now() or date_time_end < date_time_start :
                raise ValueError(f'Вы неправильно ввели даты.')
        else:
            date_time_end = datetime.datetime.now()
            date_time_start = date_time_end - datetime.timedelta(days=90)

    # Введена только одна из двух дат
    else:
        raise ValueError('Данные введены не в полном объеме. Попробуйте еще раз.')

    # Получение словаря со всеми значениями валют за выбранный период
    valute_dict = get_currency_dict(date_time_start, date_time_end)

    print(f'Показаны результаты за период {date_time_start.strftime("%d.%m.%Y")} - {date_time_end.strftime("%d.%m.%Y")} ')
    print('___________________________________________\n')

    # Вывод максимальных значений
    print_result(max_valutes_value(valute_dict), 'Max')
    print('___________________________________________\n')

    # Вывод минимальных значений
    print_result(min_valutes_value(valute_dict), 'Min')
    print('___________________________________________\n')

    # Вывод средних значений
    print_result(average_rub_course(valute_dict), 'average')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-start', nargs='?', default=None)
    parser.add_argument('-end', nargs='?', default=None)
    namespace = parser.parse_args(sys.argv[1:])

    main(start=namespace.start, end=namespace.end)
