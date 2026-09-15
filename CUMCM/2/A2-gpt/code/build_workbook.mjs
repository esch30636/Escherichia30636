import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(await fs.readFile(path.join(root,'data/workbook_values.json'),'utf8'));
const original=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'data/result2_template.xlsx')));
const log=[(await original.inspect({kind:'sheet',include:'id,name',maxChars:1200})).ndjson];
const templatePreview=await original.render({sheetName:'温度',range:'A1:F5',scale:1.5,format:'png'});
await fs.writeFile(path.join(root,'verification/template_preview.png'),new Uint8Array(await templatePreview.arrayBuffer()));
const wb=Workbook.create();
for(const name of ['温度','水分浓度']){
  const sh=wb.worksheets.add(name);
  const rows=[['时间\\到药材中心的距离',...data.radius_cm],...data.time_s.map((t,i)=>[t,...data[name][i]])];
  if(rows.length!==10801||rows.some(r=>r.length!==22))throw new Error('Incorrect output shape');
  sh.getRange('A1:V10801').values=rows;
  sh.getRange('A1:V10801').format.font={name:'Arial',size:10,color:'#172033'};
  sh.getRange('A1:V10801').format.rowHeight=19;
  sh.getRange('A1:V1').format={fill:'#17365D',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:30};
  sh.getRange('A1:A10801').format.columnWidth=34;
  sh.getRange('B1:V10801').format.columnWidth=12;
  sh.getRange('B2:V10801').setNumberFormat('0.0000');
  sh.getRange('B1:V1').setNumberFormat('0.0');
  sh.getRange('A2:A10801').setNumberFormat('0');
  sh.getRange('A1:V1').format.horizontalAlignment='center';
  sh.getRange('A2:V10801').format.horizontalAlignment='right';
  sh.getRange('A1:V10801').format.verticalAlignment='center';
  sh.getRange('A2:A10801').format.fill='#F0F4F8';
  sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(1);sh.showGridLines=false;
}
wb.recalculate();
for(const name of ['温度','水分浓度']){
  log.push((await wb.inspect({kind:'table',range:`'${name}'!A1:G4`,include:'values',tableMaxRows:4,tableMaxCols:7,maxChars:1600})).ndjson);
  for(const [part,range] of [['start','A1:G8'],['end','P10795:V10801']]){
    const blob=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
    await fs.writeFile(path.join(root,`verification/workbook_${name}_${part}.png`),new Uint8Array(await blob.arrayBuffer()));
  }
}
log.push((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:1500})).ndjson);
await fs.writeFile(path.join(root,'verification/workbook_inspect.txt'),log.join('\n'));
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'result2.xlsx'));
// Delete only the exporter-generated diagnostic sidecar; compact checks remain.
await fs.rm(path.join(root,'result2.xlsx.inspect.ndjson'),{force:true});
console.log('Exported 2 sheets, 10800 x 21 results per sheet.');
