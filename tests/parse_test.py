from bs4 import  BeautifulSoup

with open("test.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")


def parse_lv_1(catalog_name="pathway"):
    # pathway 顶级 的写法
    try:
        div_soup = soup.select_one("div.pathway_list")
        ul = div_soup.ul
        sub_catalog = []
        if ul:
            for a in ul.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)  # 去除空格和换行
                sub_catalog.append({
                    "title": text,
                    "link": href,
                    "children": []
                })
        return {
            "catalog":{
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": sub_catalog
            }
        }
    except:
        print("error")

print(parse_lv_1())