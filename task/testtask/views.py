import os
import sqlite3

from django.http import HttpResponse, JsonResponse
from django.views import View


class SQLiteMixin:

    @staticmethod
    def load_sql_data() -> dict:
        path_sqlite_db = '../task.sqlite3'
        DIRNAME = os.path.dirname(__file__)
        sql_dict = dict()
        con = sqlite3.connect(os.path.join(DIRNAME, path_sqlite_db))
        try:
            cursor_obj = con.cursor()
            cursor_obj.execute('''
                                SELECT categories.id AS id, categories.name AS name, 
                                SUM(stuff.cost) OVER (PARTITION BY stuff.category_id) AS amount, 
                                stuff.name AS stuff_name 
                                FROM categories JOIN stuff ON stuff.category_id=categories.id 
                                ORDER BY categories.id;
                                ''')
            tree = cursor_obj.fetchall()
            cursor_obj.execute('SELECT id, name, cost FROM stuff ORDER BY category_id;')
            stuffs = cursor_obj.fetchall()
        finally:
            con.close()
        for row, stuff in zip(tree, stuffs):
            if sql_dict.get(row[1]) and row[3] == stuff[1]:
                sql_dict[row[1]]['stuff'].append({'id': stuff[0], 'name': stuff[1], 'cost': stuff[2]})
            elif row[3] == stuff[1]:
                sql_dict.update({row[1]: {'id': row[0],
                                          'name': row[1],
                                          'amount': row[2],
                                          'stuff': [
                                                 {'id': stuff[0], 'name': stuff[1], 'cost': stuff[2]},
                                          ]}})
            else:
                raise SyntaxError
        return sql_dict

    def sql_data_to_html(self):
        sql_data = self.load_sql_data()
        output_to_page = ''
        for key, value in sql_data.items():
            http_output_list = ''.join(f'<li>{stuff_name["name"]}</li>' for stuff_name in value['stuff'])
            http_output_list += f'<li>amount - {value["amount"]}</li>'
            output_to_page += f'<h3>{key}</h3><ul>{http_output_list}</ul>'
        return output_to_page

    def sql_data_to_json(self):
        sql_data = self.load_sql_data()
        pseudo_json = {'categories': []}
        for key, value in sql_data.items():
            pseudo_json['categories'].append(value)
        return pseudo_json


class IndexHTMLView(View, SQLiteMixin):

    def get(self, request, *args, **kwargs):
        output_to_page = self.sql_data_to_html()
        return HttpResponse(output_to_page)


class IndexJsonView(View, SQLiteMixin):

    def get(self, request, *args, **kwargs):
        pseudo_json = self.sql_data_to_json()
        return JsonResponse(pseudo_json)
