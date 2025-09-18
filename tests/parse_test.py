from bs4 import  BeautifulSoup

with open("test.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")


def parse_list__cls_hot_list():
    try:
        item_soups = soup.find_all("div", class_="hot-list")[1:]
        sub_catalog = []
        for item_soup in item_soups:
            title = item_soup.find("h2").get_text(strip=True)
            link = ""
            list_main_soup = item_soup.find("div", class_="list-main")
            children_soups = list_main_soup.find_all("a")
            child_data = []
            for child in children_soups:
                sub_link = child.get("href")
                sub_title = child.get_text(strip=True)
                child_data.append({
                    "title": sub_title,
                    "link": sub_link,
                    "type": "category",
                    "children": []
                })
            sub_catalog.append({
                "title": title,
                "link": link,
                "type": "group",
                "children": child_data
            })
        return sub_catalog

    except Exception as e:
        print(f"by NaturalProducts top get failed")

print(parse_list__cls_hot_list())