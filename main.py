#!/usr/bin/env python3


import requests

from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Literal

url = {
    "de": "https://www.stw-rw.de/de/mensen-und-cafeterien/speiseplaene.html",
}

def get_html(url) -> str:
    response = requests.get(url)
    return response.text

def parse_menu(html_doc: str) -> dict:
    data = dict()

    soup = BeautifulSoup(html_doc, "html.parser")

    # parse date
    date_tag = soup.find("div", id="mensa_date")
    data["date"] = date_tag.find("p").text

    # parse canteens
    data["canteens"] = []
    canteens = soup.find_all("dt", class_="mensenplan")

    for canteen in canteens:
        canteen_data = parse_canteen(canteen)
        data["canteens"].append(canteen_data)
    
    return data

def parse_canteen(canteen: Tag) -> dict:
    canteen_data = dict()
    canteen_data["name"] = canteen.find("p").text
    canteen_data["counters"] = []
    canteen_data["open"] = True

    table = canteen.parent.find("table")

    if table is None:
        canteen_data["open"] = False
    else:
        canteen_data["counters"] = parse_counters(table)
    
    return canteen_data

def parse_counters(table: Tag) -> list:
    counters = []
    for row in table.find_all("tr"):
        counter = row.find("td", class_="col_theke")

        if counter is not None:
            # start of new counter
            counter_data = dict()
            counter_data["name"] = counter.find_next("b").text
            counter_data["items"] = []
            counters.append(counter_data)
        else:
            # parse items
            item_data = parse_item(row)
            counter_data["items"].append(item_data)
    
    return counters

def parse_item(item: Tag) -> dict:
    item_data = {}

    print(item)

    columns = item.find_all("td")
    item_data["name"] = columns[0].find("b").text

    allergens = columns[0].find("span")

    if allergens is not None:
        item_data["allergens"] = allergens.text.split(" ")

    item_data["student"] = columns[1].find("b").text
    item_data["intern"] = columns[2].find("b").text
    item_data["extern"] = columns[3].find("b").text

    return item_data

def get_todays_menu(language: Literal["de"] = "de") -> str:
    html_doc = get_html(url[language])
    return parse_menu(html_doc)

def main():
    data = get_todays_menu()
    print(data)


if __name__ == "__main__":
    main()

