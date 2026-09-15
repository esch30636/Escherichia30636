import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const template=path.resolve(root,'data/result3_template.xlsx');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(template));
const sh=wb.worksheets.getItem('Sheet1');
const before=await wb.render({sheetName:'Sheet1',range:'A1:F5',scale:1.5,format:'png'});
await fs.writeFile(path.join(root,'verification/template_preview.png'),new Uint8Array(await before.arrayBuffer()));
const data=JSON.parse(await fs.readFile(path.join(root,'data/workbook.json'),'utf8'));
const last=data.rows.length+1;
sh.getRange(`A1:V${last}`).clear({applyTo:'all'});
sh.getRange('A1:V1').values=[data.header];
for(let i=0;i<data.rows.length;i+=500){
 const block=data.rows.slice(i,i+500);
 sh.getRange(`A${i+2}:V${i+1+block.length}`).values=block;
}
sh.getRange(`A1:V${last}`).format.font={name:'Arial',size:10};
sh.getRange(`A1:V${last}`).format.rowHeight=19;
sh.getRange(`A1:V${last}`).format.verticalAlignment='center';
sh.getRange(`A2:A${last}`).setNumberFormat('0');
sh.getRange(`B2:V${last}`).setNumberFormat('0.0000');
sh.getRange('B1:V1').setNumberFormat('0.0');
sh.getRange(`A1:A${last}`).format.columnWidth=25;
sh.getRange(`B1:V${last}`).format.columnWidth=10;
sh.getRange('A1:V1').format={fill:'#34495E',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},rowHeight:25};
sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(1);
wb.recalculate();
const inspect=await wb.inspect({kind:'table',range:'Sheet1!A1:G5',include:'values,formulas',tableMaxRows:5,tableMaxCols:7});
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NUM!|#NAME\\?',options:{useRegex:true,maxResults:10}});
await fs.writeFile(path.join(root,'verification/workbook_inspect.txt'),inspect.ndjson+'\n'+errors.ndjson);
for(const [label,range] of [['start','A1:H8'],['end',`A${last-5}:H${last}`]]){
 const preview=await wb.render({sheetName:'Sheet1',range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(root,`verification/workbook_${label}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'result3.xlsx'));
console.log(`Saved result3.xlsx: ${data.rows.length} rows x 21 radial values`);
