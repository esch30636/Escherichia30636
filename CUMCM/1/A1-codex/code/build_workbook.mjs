import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile, FileBlob} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(await fs.readFile(path.join(root,'data/workbook_values.json'),'utf8'));
const template=path.resolve(root,'../CUMCM2026Problems/A题/附件/附件3/result1.xlsx');
// Read the provided template; author an expanded workbook with its exact table schema.
const original=await SpreadsheetFile.importXlsx(await FileBlob.load(template));
console.log((await original.inspect({kind:'sheet',include:'id,name',maxChars:1200})).ndjson);
const wb=Workbook.create();
for(const name of ['温度','水分浓度']){
  const sheet=wb.worksheets.add(name);
  const rows=[['时间\\到药材中心的距离',...data.radius_cm],
    ...data.time_s.map((t,i)=>[t,...data[name][i]])];
  if(rows.length!==1801 || rows.some(r=>r.length!==22))throw new Error('Unexpected matrix shape');
  sheet.getRange('A1:V1801').values=rows;
  sheet.getRange('A1:V1801').format.font={name:'Microsoft YaHei',size:10,color:'#172033'};
  sheet.getRange('A1:V1801').format.rowHeight=19;
  sheet.getRange('A1:V1').format={fill:'#17365D',font:{name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'},rowHeight:30};
  sheet.getRange('A1:A1801').format.columnWidth=34;
  sheet.getRange('B1:V1801').format.columnWidth=12;
  sheet.getRange('B2:V1801').setNumberFormat('0.0000');
  sheet.getRange('B1:V1').setNumberFormat('0.0');
  sheet.getRange('A2:A1801').setNumberFormat('0');
  sheet.getRange('A1:V1').format.horizontalAlignment='center';
  sheet.getRange('A2:V1801').format.horizontalAlignment='right';
  sheet.getRange('A1:V1801').format.verticalAlignment='center';
  sheet.getRange('A2:A1801').format.fill='#F0F4F8';
  sheet.freezePanes.freezeRows(1);sheet.freezePanes.freezeColumns(1);
  sheet.showGridLines=false;
}
wb.recalculate();
const logs=[];
for(const name of ['温度','水分浓度']){
  logs.push((await wb.inspect({kind:'table',range:`'${name}'!A1:G4`,include:'values',tableMaxRows:4,tableMaxCols:7,maxChars:1800})).ndjson);
  for(const [part,range] of [['start','A1:G8'],['end','P1795:V1801']]){
    const blob=await wb.render({sheetName:name,range,scale:1.4,format:'png'});
    await fs.writeFile(path.join(root,`verification/workbook_${name}_${part}.png`),new Uint8Array(await blob.arrayBuffer()));
  }
}
logs.push((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:1500})).ndjson);
await fs.writeFile(path.join(root,'verification/workbook_inspect.txt'),logs.join('\n'),'utf8');
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'result1.xlsx'));
// The exporter creates a large diagnostic sidecar; compact checks above are retained.
await fs.rm(path.join(root,'result1.xlsx.inspect.ndjson'),{force:true});
console.log('Exported result1.xlsx: 2 sheets, 1800 x 21 values per sheet.');
