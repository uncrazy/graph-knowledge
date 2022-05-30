## Установка:

```bash
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
```

## Использование:
* Рисунок всего графа
```bash
python3 run.py -g
```
* Поиск оптимального пути (method='dijkstra')
```bash
python3 run.py -p source target weight
```
Атрибут `source` — начальная вершина графа, 
`source` — конечная, `weight` — значение веса рёбер.
Возможные значения `weight`: **time_exp** — времязатраты, 
**сomp_exp** — сложность задачи. 

Например:<sup>*</sup>

```bash
python3 run.py -p S03 "CGM|D15" time_exp
```

Во время поиска в директорию `/results` выгружается 
подробный лог найденного оптимального пути.

---
<sub>*<ins>Примечание</ins>: для того, чтобы ноды с прямым слэшем `|` не воспринимались частью вводимого скрипта, такие названия вершин экранируются кавычками.</sub>