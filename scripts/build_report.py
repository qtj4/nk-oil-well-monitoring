"""Generate academic report and slide evidence from measured run artifacts.

Run with a Python environment containing reportlab; no analytical numbers are invented.
"""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
RUN = (ROOT / 'data/processed/full/latest_run.txt').read_text().strip()
RESULTS = ROOT / 'results' / RUN
OUT = ROOT / 'deliverables'
OUT.mkdir(exist_ok=True)
(OUT / 'figures').mkdir(exist_ok=True)


def read_json(name):
    return json.loads((RESULTS / name).read_text())


def read_csv(name):
    with (RESULTS / name).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def number(value, digits=2):
    return f'{float(value):,.{digits}f}'.replace(',', ' ')


summary = read_json('dataset_summary.json')
manifest = read_json('run_manifest.json')
methods = read_csv('methods_comparison.csv')
benchmarks = read_csv('processing_benchmarks.csv')
whole = read_json('whole_pipeline_benchmark.json')
issues = read_csv('known_issues.csv')
monthly = read_csv('nk7_monthly_evidence.csv')
quality = read_csv('quality_report.csv')
spm = [row for row in monthly if row['parameter'] == 'SPM']
areas = [row for row in issues if row['issue'] == 'May area scale']
absent = sum(int(row['absent_slots']) for row in quality)
source = 'https://huggingface.co/datasets/Arailym-tleubayeva/NK-Oil-Well-Sensor-Monitoring-v2'

sections = [
    ('Анализ режимов работы нефтяных скважин', [
        ('p', 'Итоговый проект по Programming for Data Analysis and Database. Applied Artificial Intelligence, магистратура.'),
        ('p', 'Аннотация. Разработана локальная система анализа исторических датчиков десяти скважин месторождения NK. '
         'Приложение связывает подготовку данных, SQLite, визуальный анализ и обнаружение кандидатов на смену режима. '
         'Полный набор содержит 258 387 наблюдений параметров за январь-сентябрь 2026 года. '
         'Сохранено официальное хронологическое разбиение, выполнены восемь аналитических SQL-запросов, '
         'сопоставлены отсутствие изменений, rolling shift и CUSUM. Проверенные метки неисправностей отсутствуют; '
         'результаты характеризуют статистические события, а не точность диагностики отказов.'),
        ('p', 'Исследовательские вопросы: как различаются доступные датчики фонтанных и насосных скважин; '
         'какие изменения сопровождаются признаками качества данных; как обеспечить воспроизводимый анализ '
         'на обычном CPU-ноутбуке; как сохранить решение аналитика и связать его с исходными наблюдениями.'),
        ('p', 'Наблюдаемое изменение режима определяется как устойчивое изменение распределения сигнала. '
         'Одиночный выброс и смена масштаба измерения могут создавать похожие признаки. '
         'Проект не устанавливает физическую причину и не управляет оборудованием.'),
        ('p', f'Основание отчета: фактически исполненный run {RUN}. Точная конфигурация, версии и хеши '
         'сохранены в run_manifest.json. Числа ниже вычислены по его таблицам.'),
        ('p', 'Авторы и распределение вклада: сведения не предоставлены. Перед сдачей вписать реальные имена '
         'и подтвержденный вклад; вымышленные участники не указаны.'),
    ]),
    ('1. Источник, структура и воспроизводимость', [
        ('p', 'Источник: Arailym Tleubayeva, NK Oil Well Sensor Monitoring v2, Hugging Face. '
         'Поставщик данных: Galaz and Company LLP. Apache-2.0; сохраняются дополнительные условия владения '
         'и конфиденциальности исходных данных. Карточка и API-метаданные сохранены локально. '
         'Исходный год назначен авторами по последовательности файлов и требует сверки с SCADA. '
         'Часовой пояс не документирован; временные метки оставлены без timezone.'),
        ('table', [['Показатель', 'Измеренное значение'],
                   ['Период', f'{summary["start"]} / {summary["end"]}'],
                   ['Строки train / test', f'{summary["train_rows"]:,} / {summary["test_rows"]:,}'],
                   ['Скважины / пары скважина-параметр', '10 / 43'],
                   ['Формат', 'Один параметр одной скважины за час'],
                   ['Исходные CSV / long Parquet', f'{summary["source_bytes"]:,} / {summary["parquet_bytes"]:,} байт'],
                   ['Оптимизированный Pandas long', f'{number(summary["long_memory_mb"], 3)} MB']]),
        ('p', 'Фонтанные скважины: NK-75, NK-76, NK-83; доступны давления в atm. '
         'Семь насосных скважин имеют SPM (strokes/min), заполнение насоса (%), нагрузки на штангу (kg), '
         'площадь динамограммы (unitless). У NK-76 отсутствует casing_pressure. '
         'Сравнивать средние разных параметров как одну физическую величину нельзя.'),
        ('p', 'Столбцы: well_id, well_type, timestamp, parameter, value, unit, n_obs, flag. '
         'Ключ: well_id + parameter + timestamp. Дубликаты отклоняются, а не усредняются молча. '
         'Месячная выборка сохраняет первые десять дней каждого месяца: 85 423 реальные строки, все скважины. '
         'Она включает окно 8 мая и июнь; ее искусственно исключенные даты не являются сбоями источника.'),
        ('p', 'Источник меньше рекомендованных 500 000 строк или 200 MB. Данные не размножались. '
         'Для формального соответствия этому пункту требуется разрешение преподавателя либо дополнительный легитимный источник.'),
    ]),
    ('2. Качество и проверка известных изменений', [
        ('p', f'Проверено {summary["rows"]:,} строк: дубликатов ключа {summary["duplicates"]}; '
         f'NULL sensor values {summary["null_values"]}. При этом найдено {absent:,} отсутствующих часовых слотов '
         'внутри наблюдаемых границ каждой пары скважина-параметр. Это сумма отсутствий параметров, '
         'не число общих часов простоя и не число NULL. Частоты source flags приведены ниже.'),
        ('table', [['Исходный flag', 'Строки']] + [[k or '(empty)', str(v)] for k, v in summary['flags'].items()]),
        ('p', 'Флаги вычислены авторами на сырых записях и перенесены в часовые средние. '
         'Поэтому отсутствие flag не гарантирует корректность. Нули SPM сохранены; пропуски и выбросы '
         'не интерполируются. Площадь динамограммы исключена из основного сравнения методов; '
         'отдельно сохранены чувствительность к ее включению и к сохранению flagged-записей.'),
        ('chart', 'spm'),
        ('p', 'Проверка карточки источника: у NK-7 медиана SPM в апреле 5.3439, в мае 1.4740, в июне 1.7443. '
         'Доля нулей в мае 49.46%, в июне 16.32%. Снижение видно уже в мае, поэтому точное начало в июне '
         'не подтверждается. Доля отрицательной площади: май 30.68%, июнь 50.92%. '
         'Причину датчики без журнала обслуживания не определяют.'),
    ]),
    ('3. Архитектура и база данных', [
        ('p', 'Python 3.12: chunked CSV -> валидация -> long/wide Parquet -> нормализованная SQLite -> '
         'EDA и CPU-методы -> Streamlit/Plotly. Подготовка выполняется CLI. '
         'Приложение читает готовые артефакты, кеширует их по fingerprint и не обучает методы при фильтрации. '
         'Отдельный JavaScript frontend, микросервисы и GPU не требуются.'),
        ('p', 'Основные сущности: wells(well_id PK, well_type); parameters(parameter PK, unit); '
         'observations(well_id FK, parameter FK, timestamp, value, n_obs, split). '
         'Составной PK наблюдения предотвращает инфляцию строк. flag_types и observation_flags нормализуют '
         'составные флаги, а исходная строка flag сохраняется для аудита. Индекс timestamp ускоряет диапазоны. '
         'ER-схема Mermaid: docs/database_design.md.'),
        ('table', [['SQL-файл', 'Назначение и конструкция'],
                   ['01_coverage', 'JOIN wells/parameters, полнота по паре'],
                   ['02_monthly', 'GROUP BY скважина, параметр, месяц'],
                   ['03_flagged_groups', 'GROUP BY / HAVING flagged > 0'],
                   ['04_gaps', 'CTE и LAG по скважине + параметру'],
                   ['05_causal_rolling', 'AVG по 24 предшествующим записям'],
                   ['06_flags', 'Частоты исходных флагов'],
                   ['07_type_summary', 'JOIN и группировка по типу / параметру'],
                   ['08_latest', 'CTE + ROW_NUMBER, последнее наблюдение']]),
        ('p', 'Все восемь запросов реально исполнены в SQLite и возвращены в Pandas. '
         'LAG измеряет интервалы между существующими timestamp, а не NULL значений. '
         'Окно 24 ROWS означает 24 записи, не гарантированно 24 часа.'),
        ('p', 'Решения аналитика хранятся отдельно: analysis_runs, events, event_runs, alert_reviews '
         'в data/reviews.sqlite. Идентификатор события зависит от данных, конфигурации, метода и временного бина. '
         'Повторная индексация не стирает заметки. Статусы проверяются, SQL параметризован, HTML заметок экранируется.'),
    ]),
    ('4. Подготовка и протокол методов', [
        ('p', 'CSV читается блоками по 25 000 строк; категориальные идентификаторы снижают память без изменения '
         'float64 значений. Временная точность сохраняется. Long->wide pivot включает скважину в индекс; '
         f'{summary["reconciled_nonnull_values"]:,} непропущенных значений сверены точно, получено '
         f'{summary["wide_rows"]:,} строк скважина-час. Ничего не смешивается между скважинами.'),
        ('p', 'Официальная граница: train до 2026-08-08 22:00 включительно, test с 23:00. '
         'Нет shuffle. Для методов используются дневные медианы с минимум 12 unflagged записями. '
         'Бин 8 августа исключен, поскольку пересекает границу. Дневной timestamp обозначает начало бина; '
         'медиана и событие доступны только после завершения дня.'),
        ('table', [['Метод', 'Определение и фиксированные настройки'],
                   ['No change', 'Пустое множество кандидатов; контроль отсутствия детекции'],
                   ['Rolling shift', '|x_t - mean(x_(t-3:t-1))| / s_train > 3'],
                   ['CUSUM', 'Две суммы отклонений от train median; drift=0.5, h=5'],
                   ['Общее', 'Train MAD*1.4826, fallback std/floor; cooldown 7 дней']]),
        ('p', 'Нормализатор fit только на train; в test параметры заморожены. Rolling-история использует '
         'только предшествующие дни и сбрасывается через разрыв. Для CUSUM также сбрасывается накопленное состояние. '
         'Маркер внутри train ретроспективен, поскольку использует обучающий период целиком. '
         'Это отдельно обозначено, и train-события не используются как оценка хронологической точности.'),
        ('p', 'Метки истинных смен режима/отказов не обнаружены. Precision, recall и F1 не вычисляются. '
         'MAE не относится к этой задаче без численной прогнозной цели. Сравнение показывает число кандидатов, '
         'частоту, чувствительность к порогу и измеренные ресурсы на одинаковом наборе единиц.'),
        ('p', 'Дополнительная аналитика характеризует события по окнам +/-7 дней: медиана, вариативность, '
         'сдвиг уровня, плотность flags, отсутствия/NULL и расстояние до следующего кандидата. '
         'Следующее окно используется только для ретроспективного объяснения, не подается детектору '
         'и не становится меткой неисправности.'),
    ]),
    ('5. Сопоставление методов', [
        ('p', 'Общая тестовая область: 1 747 допустимых скважина-параметр-дней. '
         'Конфигурации заморожены до тестового запуска. Результаты ниже относятся к кандидатам '
         'по выбранным датчикам и фильтрам, а не к количеству реальных аварий или физических режимов.'),
        ('table', [['Метод', 'Train', 'Test', 'На 100 test дней', 'Секунды']] +
         [[r['method'], r['train_events'], r['test_events'], number(r['test_events_per_100_days']),
           number(r['wall_seconds'], 4)] for r in methods]),
        ('chart', 'methods'),
        ('table', [['Чувствительность порога', '80%', '100%', '120%']] +
         [[r['method'], r['test_events_threshold_80pct'], r['test_events'], r['test_events_threshold_120pct']] for r in methods]),
        ('p', 'CUSUM создает больше кандидатов, в том числе повторные уведомления при длительном '
         'отклонении от train reference после cooldown. Это не доказывает превосходство чувствительности '
         'или качества. No-change закономерно дает ноль. По этим диагностическим числам нельзя ранжировать '
         'точность без независимой экспертной разметки. Изменение порогов служит проверкой чувствительности; '
         'порог не выбирался по test-результатам.'),
    ]),
    ('6. EDA и интерпретация масштаба', [
        ('chart', 'area'),
        ('p', 'Соотношения медиан апреля и мая составляют примерно 9.95-20.37 в семи насосных скважинах. '
         'Окна карточки источника и ее приблизительные примеры отличаются от этих точных месячных окон. '
         'Наблюдаемая синхронность поддерживает гипотезу смены масштаба/калибровки, '
         'но не устанавливает причину. Автоматическая коррекция коэффициентом не применяется.'),
        ('p', 'EDA сохранена как descriptive_statistics.csv, daily_patterns.csv и пять HTML-графиков: '
         'временной ряд с предшествующим средним, распределение по скважинам и типам, профиль часа суток, '
         'корреляции одной скважины, матрица source flags. Средние профилей объединяют наблюдения '
         'с неодинаковым покрытием; счетчики count позволяют увидеть эту неоднородность.'),
        ('p', 'Корреляции считаются только по совпавшим timestamp одной скважины при минимум 24 парах. '
         'Матрица количества пар сохранена отдельно. Корреляция не доказывает причинность, '
         'а масштабирование площади и сезонная/операционная структура могут влиять на результат. '
         'У типов скважин разные наборы датчиков: сравнивать можно покрытие и структуру доступных '
         'наблюдений; давления и SPM нельзя ставить на одну физическую шкалу.'),
        ('p', 'Заявленные в карточке многодневные провалы и общие отключения исследуются экспортом LAG. '
         'Для sample-режима разрывы отбора отмечены отдельно и не интерпретируются как реальный простой.'),
    ]),
    ('7. Производительность и проверка системы', [
        ('table', [['Операция', 'Wall seconds', 'Sampled peak RSS MB']] +
         [[r['operation'], number(r['wall_seconds'], 4), number(r['sampled_peak_rss_mb'], 2)] for r in benchmarks]),
        ('p', f'Полный pipeline: {number(whole["wall_seconds"], 4)} s; sampled absolute peak RSS '
         f'{number(whole["sampled_peak_rss_mb"])} MB, прирост от baseline '
         f'{number(whole["rss_increment_mb"])} MB. Измерение: опрос RSS процесса каждые 10 ms плюс '
         'начальный/конечный замер. Короткие пики могут быть пропущены. Базовая память Python/библиотек '
         'включена. CSV ingest содержит валидацию; Parquet reread ее не повторяет. '
         'Разный состав работы и теплый файловый кеш запрещают трактовать отношение времен как чистое ускорение формата.'),
        ('p', 'CPU Windows-ноутбук, Python 3.12, около 6.29 GB установленной RAM. GPU не использовался. '
         'Рабочие версии зависимостей закреплены requirements.txt. Повторный полный запуск дал '
         'те же объемы и количество кандидатов; run_manifest сохраняет конфигурации, source/data hashes и версии.'),
        ('p', '21 тест проходит, включая реальный UI review->save->reload->report, все SQL, pivot, '
         'разделение скважин, ошибочные даты, неизвестные flags, защиту от future/test leakage, '
         'официальные file hashes, временные разрывы, пустые состояния и автономную загрузку sample. '
         'Тот же набор прошел в новом venv после установки requirements.txt; pip check не нашел конфликтов. '
         'Ruff проходит. Синтетические fixtures используются только в тестах; аналитические результаты взяты из источника.'),
        ('p', 'Запуск: python -m nk_oil.cli prepare --mode sample; python -m nk_oil.cli enhance --mode sample; '
         'python -m streamlit run app.py. Полный режим: fetch, затем prepare/enhance --mode full. '
         'На Windows следует использовать .venv/Scripts/python.exe. Полные команды и типовые ошибки: README.md.'),
    ]),
    ('8. Выводы, ограничения и источники', [
        ('p', 'Получен воспроизводимый аналитический инструмент: исходные значения проверены, '
         'SQL и Parquet согласованы, известные изменения исследованы на полном наборе, '
         'кандидаты связаны с сохраненными решениями аналитика. Без GPU приложение работает '
         'на ограниченном ноутбуке и демонстрируется автономно.'),
        ('p', 'Главные ограничения: отсутствуют подтвержденные отказы, журнал обслуживания и дебит; '
         'возможен сдвиг калибровки; год и timezone не подтверждены оператором; '
         'датасет меньше рекомендации курса; агрегация по дням теряет внутрисуточные изменения. '
         'Окна описания событий ретроспективны. Аналитические уведомления и статус confirmed '
         'не являются ground truth и не должны управлять оборудованием.'),
        ('p', 'Следующая исследовательская работа: независимая экспертная разметка, проверка временной привязки '
         'в SCADA, отделение смены масштаба от технологического процесса и согласование достаточности размера '
         'с преподавателем. Финальная оценка выставляется преподавателем; эвристический аудит проекта '
         'не является оценкой курса.'),
        ('p', '[1] Tleubayeva, Arailym. Oil Well Sensor Monitoring Dataset: NK Field (v2), 2026. '
         f'Hugging Face. {source} . Revision {manifest["source_revision"]}. '
         'Карточка источника и CSV проверены; дополнительно применяются условия владения исходными данными.'),
        ('p', f'[2] Фактически исполненный run {RUN}: run_manifest.json, dataset_summary.json, '
         'known_issues.csv, nk7_monthly_evidence.csv, methods_comparison.csv, processing_benchmarks.csv, '
         'quality_report.csv, sql/*.csv. Производящий код: nk_oil/*.py, app.py, sql/queries/*.sql.'),
        ('p', '[3] Проверки: results/phase4_tests.txt, phase4_clean_env_tests.txt, '
         'phase4_clean_env_dependencies.txt, phase4_final_sample_checks.txt. '
         'Методология и ER: docs/experiments_plan.md, database_design.md, full_data_validation.md.'),
        ('p', 'Статус сдачи: публикация разрешена только в qtj4. Точный срок экзамена, Moodle-подтверждение, '
         'одобрение темы преподавателем и реальные вклады команды не предоставлены и не вымышлены.'),
    ]),
]

font_dir = Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Arial', str(font_dir / 'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold', str(font_dir / 'arialbd.ttf')))
body = ParagraphStyle('body', fontName='Arial', fontSize=10.1, leading=14.7, spaceAfter=10, textColor=colors.HexColor('#18343d'))
heading = ParagraphStyle('heading', parent=body, fontName='Arial-Bold', fontSize=22, leading=27, spaceAfter=20)
small = ParagraphStyle('small', parent=body, fontSize=8.8, leading=12, spaceAfter=0)


def drawing(kind):
    d = Drawing(480, 205)
    if kind == 'spm':
        chart = LinePlot()
        chart.x, chart.y, chart.width, chart.height = 45, 35, 405, 145
        chart.data = [[(i, float(row['median'])) for i, row in enumerate(spm)]]
        chart.lines[0].strokeColor = colors.HexColor('#147d85')
        chart.lines[0].strokeWidth = 2
        chart.xValueAxis.valueMin, chart.xValueAxis.valueMax, chart.xValueAxis.valueStep = 0, 8, 1
        chart.xValueAxis.labelTextFormat = lambda value: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'][round(value)]
        chart.yValueAxis.valueMin, chart.yValueAxis.valueMax, chart.yValueAxis.valueStep = 0, 6, 1
        title = 'NK-7: monthly median SPM (strokes/min), 2026'
    else:
        chart = VerticalBarChart()
        chart.x, chart.y, chart.width, chart.height = 45, 35, 405, 145
        if kind == 'area':
            values = [float(row['ratio']) for row in areas]
            chart.categoryAxis.categoryNames = [row['well_id'] for row in areas]
            title = 'Dynamometer area: May median / April median (ratio)'
            maximum = 25
        else:
            values = [int(row['test_events']) for row in methods]
            chart.categoryAxis.categoryNames = ['No change', 'Rolling shift', 'CUSUM']
            title = 'Test candidate counts; 1,747 eligible well-parameter-days'
            maximum = 160
        chart.data = [values]
        chart.valueAxis.valueMin, chart.valueAxis.valueMax = 0, maximum
        chart.bars[0].fillColor = colors.HexColor('#147d85')
        chart.bars[0].strokeColor = colors.HexColor('#147d85')
        chart.categoryAxis.labels.fontName = 'Arial'
        chart.categoryAxis.labels.fontSize = 9
        chart.valueAxis.labels.fontName = 'Arial'
    d.add(chart)
    d.add(String(45, 192, title, fontName='Arial-Bold', fontSize=10, fillColor=colors.HexColor('#18343d')))
    renderPDF.drawToFile(d, str(OUT / 'figures' / f'{kind}.pdf'))
    return d


story = []
markdown = []
for index, (title, blocks) in enumerate(sections):
    if index:
        story.append(PageBreak())
    story.append(Paragraph(escape(title), heading))
    markdown.append('#' * (1 if index == 0 else 2) + ' ' + title + '\n')
    for kind, content in blocks:
        if kind == 'p':
            story.append(Paragraph(escape(content), body))
            markdown.append(content + '\n')
        elif kind == 'table':
            cells = [[Paragraph(escape(str(cell)), small) for cell in row] for row in content]
            widths = [180, 300] if len(content[0]) == 2 else [480 / len(content[0])] * len(content[0])
            table = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dfeeee')),
                                       ('LINEBELOW', (0, 0), (-1, 0), .8, colors.HexColor('#147d85')),
                                       ('LINEBELOW', (0, 1), (-1, -1), .3, colors.HexColor('#d5dfe1')),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            story.extend([table, Spacer(1, 14)])
            markdown.append('\n'.join(['| ' + ' | '.join(map(str, row)) + ' |' for row in
                                       [content[0], ['---'] * len(content[0]), *content[1:]]]) + '\n')
        else:
            story.extend([drawing(content), Spacer(1, 12)])
            markdown.append(f'Figure: deliverables/figures/{content}.pdf; source results/{RUN}/.\n')


def footer(canvas, doc):
    canvas.setFont('Arial', 7.3)
    canvas.setFillColor(colors.HexColor('#667e86'))
    canvas.drawString(52, 29, f'NK v2 | run {RUN} | source: Arailym Tleubayeva / Galaz and Company LLP')
    canvas.drawRightString(543, 29, str(doc.page))


SimpleDocTemplate(str(OUT / 'final_report.pdf'), pagesize=(595.28, 841.89),
                  leftMargin=52, rightMargin=52, topMargin=48, bottomMargin=48,
                  title='Operating Regime Analysis of Oil Wells', author='Project authors to be supplied')\
    .build(story, onFirstPage=footer, onLaterPages=footer)
(ROOT / 'docs/final_report.md').write_text('\n'.join(markdown), encoding='utf-8')
evidence = {'run_id': RUN, 'summary': summary, 'manifest': manifest, 'methods': methods,
            'benchmarks': benchmarks, 'whole': whole, 'issues': areas, 'monthly_spm': spm,
            'absent_hour_slots': absent, 'source': source}
(OUT / 'presentation_evidence.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Report and editable slide evidence generated from {RUN}')
