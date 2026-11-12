import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const workspaceDir = path.resolve('../..');
const project = path.join(workspaceDir, 'outputs/nk_oil');
const out = path.join(project, 'deliverables');
const SKILL_DIR = 'C:/Users/LAPTOPE/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations';
const RUNTIME_PYTHON = 'C:/Users/LAPTOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {finalizePresentation, applyPresentationChartFont} = await import(pathToFileURL(path.join(SKILL_DIR, 'container_tools/artifact_tool_utils.mjs')).href);
const e = JSON.parse(await fs.readFile(path.join(out, 'presentation_evidence.json'), 'utf8'));
const p = Presentation.create({slideSize:{width:1280,height:720}});
const ink='#18343d', teal='#147d85', rust='#b4512e', paper='#f7f4ed', muted='#5e747c';

function text(s, value, x,y,w,h, size=30, color=ink, bold=false){
  const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=value;
  sh.text.style={fontFamily:'Arial',fontSize:size,color,bold};
  return sh;
}
function base(title, source, notes){
  const s=p.slides.add(); s.background.fill=paper;
  text(s,title,70,48,1140,100,44,ink,true);
  text(s,`NK v2 · ${e.run_id} · ${p.slides.items.length}`,70,664,1140,36,16,muted);
  s.speakerNotes.text=`${notes}\nИсточник: ${source}\nRun: results/${e.run_id}/. Source dataset: ${e.source}, revision ${e.manifest.source_revision}. Historical observations; no verified failure labels.`;
  return s;
}
function block(s,label,x,y,w=255,h=100){
  const sh=s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:'#e3eeeb',line:{fill:teal,width:1}});
  sh.text=label; sh.text.style={fontFamily:'Arial',fontSize:27,color:ink,bold:true};
  return sh;
}
function arrow(s,x,y){s.shapes.add({geometry:'rightArrow',position:{left:x,top:y,width:26,height:24},fill:teal,line:{fill:'none',width:0}});}
function chart(s,type,cats,values,title,{x=70,y=175,w=830,h=410,max,format='0',labels=false}={}){
  const c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},title,
    titleTextStyle:{fontSize:22,fill:ink},categories:cats,
    series:[{name:title,values:values.map(v=>Number(v.toFixed(6))),smooth:false,fill:teal,line:{fill:teal,width:3,style:'solid'},marker:{symbol:'circle',size:7,fill:teal}}],
    lineOptions:{smooth:false},
    hasLegend:false,chartFill:paper,plotAreaFill:paper,
    barOptions:{direction:'column',grouping:'clustered',gapWidth:95},
    xAxis:{textStyle:{fontSize:22,fill:ink},line:{fill:muted,width:1,style:'solid'}},
    yAxis:{min:0,...(max ? {max}:{}),numberFormatCode:format,textStyle:{fontSize:20,fill:ink},
      majorGridlines:{fill:'#dce4e1',width:1,style:'solid'}},
    dataLabels:{showValue:labels,position:'outEnd',numberFormatCode:format,textStyle:{fontSize:21,fill:ink}}});
  applyPresentationChartFont(c,{fontFamily:'Arial'}); return c;
}

let s=base('Анализ режимов\nнефтяных скважин','docs/project_scope.md','15 секунд. Исследование исторических датчиков. Не диагностика подтвержденных отказов.');
s.shapes.items[0].position={left:70,top:135,width:1135,height:205};
s.shapes.items[0].text.style={fontFamily:'Arial',fontSize:64,color:ink,bold:true};
text(s,'NK Oil Well Sensor Monitoring v2',74,375,1090,55,32,teal);
text(s,'Python · SQLite · Streamlit\nИсторические данные / локальный CPU',74,465,1090,100,30,muted);

s=base('Данные и официальное разбиение','dataset_summary.json; data/raw/dataset_card.md','25 секунд. Проверены 258387 строк, 10 скважин, 43 пары. Год и timezone требуют проверки оператором.');
chart(s,'bar',['Train','Test'],[e.summary.train_rows,e.summary.test_rows],'Наблюдения параметров (строки)',{max:240000,labels:true});
text(s,'258 387 строк\n10 скважин\n3 фонтанные / 7 насосных',935,190,285,190,30,teal,true);
text(s,'Январь-сентябрь 2026\nГраница test:\n8 августа, 23:00',935,425,285,150,28);
text(s,'Разные типы скважин имеют разные датчики и единицы. Размер источника ниже рекомендации курса.',75,610,1130,45,23,rust);

s=base('Локальная архитектура','nk_oil/pipeline.py; app.py; docs/architecture.md','25 секунд. CLI формирует неизменяемые результаты, UI читает кеш по версии. GPU не нужен.');
const labels=['CSV\n25 000 строк/блок','Проверка\nLong / wide Parquet','SQLite + EDA\nCPU-детекторы','Streamlit\n7 разделов'];
labels.forEach((a,i)=>{block(s,a,70+i*290,215,255,120); if(i<3)arrow(s,331+i*290,264);});
text(s,'Подготовка: CLI, не импорт приложения',75,390,1100,50,34,teal,true);
text(s,'Сырые значения сохраняются. Pivot включает well_id и timestamp.\nКаждое непропущенное значение long/wide сверено точно.\nФильтры UI читают выбранную скважину и период из SQLite.',75,465,1120,150,29);

s=base('SQLite: нормализация и восемь запросов','sql/queries/*.sql; nk_oil/database.py; docs/database_design.md','35 секунд. Отдельные измерения wells и parameters, составной ключ observations. Флаги нормализованы. Все восемь запросов возвращены в Pandas.');
block(s,'wells\nwell_id PK',70,180,260,95); block(s,'observations\nwell + parameter + time PK',410,180,445,95); block(s,'parameters\nparameter PK',940,180,270,95);
arrow(s,355,213); arrow(s,885,213);
text(s,'LAG(timestamp) OVER (\n  PARTITION BY well_id, parameter\n  ORDER BY timestamp\n)',75,330,720,190,28,teal);
text(s,'JOIN · GROUP BY/HAVING\nCTE · LAG · ROW_NUMBER\nAVG по 24 предыдущим\nзаписям',840,330,365,210,24);
text(s,'Отсутствующий час и NULL значения - разные случаи.\nFlags: отдельные flag_types / observation_flags; исходная строка сохранена.',75,565,1130,85,27);

s=base('Качество: флаги не заменяют проверку','dataset_summary.json; quality_report.csv; sql/04_gaps.csv','30 секунд. 7041 flagged строк. 21014 отсутствующих pair-hour внутри endpoints, не общее время простоя. NULL=0 не означает полной сетки.');
const flagrows=[['Исходный flag','Строки'],...Object.entries(e.summary.flags).filter(([k])=>k).map(([k,v])=>[k,String(v)])];
const table=s.tables.add({rows:flagrows.length,columns:2,left:75,top:180,width:800,height:345,columnWidths:[610,190],values:flagrows});
for(let r=0;r<flagrows.length;r++)for(let c=0;c<2;c++){
  const cell=table.getCell(r,c); cell.fill=r===0?'#dfeeee':paper;
  cell.text.style={fontFamily:'Arial',fontSize:25,color:ink,bold:r===0};
}
table.borders.assign({fill:'#d2ddda',width:1,style:'solid'});
text(s,'0 дубликатов ключа\n0 NULL sensor values\n21 014 отсутствий\nпараметр-час',920,190,300,230,28,teal,true);
text(s,'Без интерполяции. Нули SPM сохранены. В sample пропуски отбора отмечены отдельно.\nФлаг часа отражает хотя бы одну подозрительную исходную запись.',75,565,1130,85,26);

s=base('Площадь динамограммы меняет масштаб в мае','known_issues.csv; nk_oil/analytics.py','35 секунд. Точные месячные окна, разное покрытие. Изменение масштаба наблюдается, причина калибровки не доказана. В главных детекторах площадь исключена.');
chart(s,'bar',e.issues.map(r=>r.well_id),e.issues.map(r=>+r.ratio),'Медиана мая / медиана апреля (раз)',{max:25,format:'0.0',labels:true,w:870});
text(s,'9.95-20.37 раза\nпо семи скважинам',970,195,250,150,30,teal,true);
text(s,'Возможна\nкалибровка.\nПричина неизвестна.',970,380,250,195,26,rust);
text(s,'Основные методы исключают этот параметр; отдельные sensitivity-экспорты сохраняют его влияние.',75,610,1120,45,23);

s=base('NK-7: снижение SPM видно уже в мае','nk7_monthly_evidence.csv; source card Known issues','40 секунд. Карточка говорит о поведении с июня, но данные показывают более раннее снижение. Месячная агрегация не датирует точный change point.');
chart(s,'line',['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен'],e.monthly_spm.map(r=>+r.median),'Месячная медиана SPM (strokes/min)',{max:6,format:'0.0',w:865});
text(s,'Апрель  5.34\nМай       1.47\nИюнь    1.74',970,200,250,180,32,teal,true);
text(s,'Нули SPM:\nмай 49.46%\nиюнь 16.32%',970,420,250,150,28);
text(s,'Снижение видно в мае. Причина и точная дата смены режима не установлены.',75,610,1120,45,23,rust);

s=base('Три метода и контроль временной утечки','nk_oil/methods.py; run_manifest.json; tests/test_analysis.py','35 секунд. Дневная медиана доступна после конца дня. Нормализация train-only; train markers ретроспективны, test frozen. 8 августа исключен.');
text(s,'No change',75,185,300,55,34,teal,true); text(s,'Нет кандидатов; контроль отсутствия детекции',400,188,800,55,29);
text(s,'Rolling shift',75,285,300,55,34,teal,true); text(s,'Отклонение от предыдущих 3 дней / s_train > 3',400,288,800,70,29);
text(s,'CUSUM',75,395,300,55,34,teal,true); text(s,'Две накопленные суммы; drift=0.5, h=5',400,398,800,60,29);
text(s,'Медиана и MAD только на train. Не менее 12 unflagged записей/день.\nCooldown 7 дней; история сбрасывается через разрыв. Бин 8 августа исключен.',75,515,1120,100,28);

s=base('Кандидаты различаются; точность неизвестна','methods_comparison.csv; events.csv','40 секунд. 1747 test well-parameter-days. У CUSUM могут повторяться уведомления о стойком отклонении от reference. Counts не доказывают лучшую точность.');
chart(s,'bar',['No change','Rolling shift','CUSUM'],e.methods.map(r=>+r.test_events),'Кандидаты на test: 1 747 скважина-параметр-дней',{max:160,labels:true,w:820});
text(s,'0 / 29 / 139',930,195,300,75,39,teal,true);
text(s,'Порог 80% / 120%:\nRolling 39 / 21\nCUSUM 148 / 125',930,330,300,150,28);
text(s,'Нет ground truth:\nprecision / recall / F1\nне вычисляются',930,510,300,110,27,rust);

s=base('Решение аналитика и отчет','nk_oil/events.py; reporting.py; tests/test_product.py','45 секунд. Живой demo: well -> signal -> candidate -> flags/coverage -> note/status -> offline HTML. confirmed не метка реального отказа.');
block(s,'Скважина\nи период',75,190,250,105); arrow(s,340,232);
block(s,'Кандидат\nи контекст',385,190,250,105); arrow(s,650,232);
block(s,'Решение\nв SQLite',695,190,250,105); arrow(s,960,232);
block(s,'HTML\nотчет',1005,190,205,105);
text(s,'Идентификатор: данные + конфигурация + метод + well/parameter/time\nПовторный анализ не удаляет прошлые заметки.\nОтчет содержит встроенный график, source/run hashes и статус.',75,365,1130,180,29);
text(s,'Окно +/-7 дней нужно только для ретроспективного объяснения.\nConfirmed - мнение аналитика, не подтвержденный отказ.',75,550,1130,110,25,rust);

s=base('Измеренная работа на CPU-ноутбуке','processing_benchmarks.csv; whole_pipeline_benchmark.json','25 секунд. Poll RSS каждые 10ms, может пропустить краткий пик; в RSS включен Python baseline. CSV включает валидацию, Parquet read не повторяет ее. Не заявлять pure speedup.');
chart(s,'bar',['CSV + validation','Pivot','SQLite','8 SQL','Parquet read'],e.benchmarks.map(r=>+r.wall_seconds),'Wall seconds (разный состав работы)',{max:3.5,format:'0.00',labels:true,w:840});
text(s,`${e.whole.wall_seconds.toFixed(2)} s\nполный pipeline`,940,195,275,150,34,teal,true);
text(s,`${e.whole.sampled_peak_rss_mb.toFixed(1)} MB\nпиковая RSS (опрос)`,940,390,275,130,29);
text(s,'21 тест проходит, включая чистый venv и UI review-to-report. GPU не использован.',75,610,1130,45,25);

s=base('Что подтверждено и что остается открытым','docs/final_report.md; docs/assumptions_and_blockers.md','25 секунд. Проверенная аналитическая система, не автоматический диагноз. Данные недостаточного размера требуют согласования. Реальные участники/срок сдачи не выдуманы.');
text(s,'Подтверждено',75,185,500,65,37,teal,true);
text(s,'Полный воспроизводимый анализ\nSQLite / 8 запросов / проверенный pivot\nОбъяснимые кандидаты и сохранение review\nАвтономный dashboard и отчет',75,280,690,250,30);
text(s,'Ограничения',825,185,370,65,37,rust,true);
text(s,'Нет меток отказов\nВозможна смена калибровки\nГод и timezone требуют сверки\nИсточник ниже порога курса',825,280,390,250,28);
text(s,'Далее: экспертная разметка и сверка данных с оператором.',75,600,1130,55,27,teal,true);

await fs.mkdir(out,{recursive:true});
const candidatePath=path.join(workspaceDir,'work/slide_build/candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(out,'final_presentation_v5.pptx');
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath,
  pythonExecutable:RUNTIME_PYTHON,
  integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','5'],
  explicitTotalSlideCount:12,requiredNativeTableOwnerSlides:[5],requiredNativeChartOwnerSlides:[2,6,7,9,11],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
  receiptPath:path.join(workspaceDir,'work/slide_build/final_v5.validation.json')});
console.log(JSON.stringify({finalPath,result}));
