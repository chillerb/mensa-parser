#!/usr/bin/env python3

url_de = "https://www.stw-rw.de/de/mensen-und-cafeterien/speiseplaene.html"
url_en = "https://www.stw-rw.de/en/mensen-und-cafeterien/speiseplaene.html"

import requests
import os

from html.parser import HTMLParser

def get_html(url):
    response = requests.get(url)
    return response.text

class Node:
    def __init__(self, tag, attrs=None, data=""):
        self.tag = tag
        self.attrs = dict(attrs) if attrs is not None else {}
        self.data = data
        self.children = []
    
    def __repr__(self):
        return f"Node({self.tag})"
    
    def __iter__(self):
        # depth first iteration
        next_nodes = [self]
        while len(next_nodes) > 0:
            node = next_nodes.pop()
            next_nodes = node.children + next_nodes
            yield node
    
class NodeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = None
        self.stack = None
    
    def feed(self, data):
        self.root = Node("root")
        self.stack = [self.root]
        return super().feed(data)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        self.stack.append(node)
    
    def handle_endtag(self, tag):
        self.stack.pop(-1)
        return super().handle_endtag(tag)

    def handle_data(self, data):
        self.stack[-1].data = data

def match_node(
    node: Node,
    tag: str = None,
    attrs: dict = None,
    data: str = None,
    subclass: str = None
):
    is_match = True
    if tag is not None:
        is_match &= node.tag == tag
    if attrs is not None:
        is_match &= node.attrs == attrs
    if data is not None:
        is_match &= node.data == data
    if subclass is not None:
        if "class" in node.attrs:
            is_match &= subclass in node.attrs["class"].split(" ")
        else:
            is_match = False
    return is_match

def find_all(
    node: Node,
    tag: str = None,
    attrs: dict = None,
    data: str = None,
    subclass: str = None
):
    matches = []
    for n in node:
        if match_node(n, tag, attrs, data, subclass):
            matches.append(n)
    return matches

def find_first(
    node: Node,
    tag: str = None,
    attrs: dict = None,
    data: str = None,
    subclass: str = None
):
    for n in node:
        if match_node(n, tag, attrs, data, subclass):
            return n
    return None

def get_menu(root: Node):
    date = get_date(root)
    print(date)
    canteens = find_all(root, subclass="mensenplan")
    print(canteens)
    for canteen in canteens:
        name_node = find_first(canteen, tag="p")
        canteen_name = name_node.data
        print(canteen_name)
        # menu_node = find_first(canteen, tag="table")
        menu_node = find_first(root, tag="table")
        for row in find_all(menu_node, tag="tr"):
            # check if it's a new counter
            column = find_first(row, tag="td")
            if match_node(column, tag="td", subclass="col_theke"):
                counter_name_node = find_first(column, tag="b")
                counter_name = counter_name_node.data
                print(counter_name)
            else:
                columns = find_all(row, tag="td")
                item_name_node = find_first(columns[0], tag="b")
                item_name = item_name_node.data
                price = find_first(columns[1], tag="b")
                print(item_name, price.data)
            

def get_date(root: Node):
    date_1 = find_first(root, attrs={"id": "mensa_date"})
    date_2 = find_first(date_1, tag="p")
    return date_2.data



def main():
    html = get_html(url_de)
    parser = NodeParser()
    parser.feed(html)

    root = parser.root
    print(root)
    get_menu(root)


if __name__ == "__main__":
    main()
