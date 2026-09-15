import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'data/result4_template.xlsx')));
const sh=wb.worksheets.getItem('Sheet1');
const template=await wb.render({sheetName:'Sheet1',range:'A1:F5',scale:1.5,format:'png'});
await fs.writeFile(path.join(root,'verification/template_preview.png'),new Uint8Array(await template.arrayBuffer()));
const data=JSON.parse(await fs.readFile(path.join(root,'data/workbook.json'),'utf8'));
const last=data.rows.length+1;
sh.getRange(`A1:W${last}`).clear({applyTo:'all'});
sh.getRange('A1:W1').values=[data.header];
for(let i=0;i<data.rows.length;i+=500){
 const block=data.rows.slice(i,i+500);
 sh.getRange(`A${i+2}:W${i+1+block.length}`).values=block;
}
sh.showGridLines=false;
sh.getRange(`A1:W${last}`).format.font={name:'Arial',size:10};
sh.getRange(`A1:W${last}`).format.rowHeight=20;
sh.getRange(`A1:W${last}`).format.verticalAlignment='center';
sh.getRange(`A2:A${last}`).setNumberFormat('0');
sh.getRange(`B2:W${last}`).setNumberFormat('0.0000');
sh.getRange('B1:V1').setNumberFormat('0.0');
sh.getRange(`A1:A${last}`).format.columnWidth=31;
sh.getRange(`B1:V${last}`).format.columnWidth=10;
sh.getRange(`W1:W${last}`).format.columnWidth=15;
sh.getRange('A1:W1').format={fill:'#34495E',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},rowHeight:28};
sh.getRange('A1:W1').format.horizontalAlignment='center';
sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(1);
wb.recalculate();
const inspect=await wb.inspect({kind:'table',range:'Sheet1!A1:G5',include:'values,formulas',tableMaxRows:5,tableMaxCols:7});
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NUM!|#NAME\\?',options:{useRegex:true,maxResults:10}});
await fs.writeFile(path.join(root,'verification/workbook_inspect.txt'),inspect.ndjson+'\n'+errors.ndjson);
for(const [label,range] of [['start','A1:H8'],['surface_start','M1:W8'],['end',`A${last-5}:H${last}`],['surface_end',`L${last-5}:W${last}`]]){
 const preview=await wb.render({sheetName:'Sheet1',range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(root,`verification/workbook_${label}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'result4.xlsx'));
// Exporter's full-cell diagnostics are redundant with the compact readback audit.
await fs.rm(path.join(root,'result4.xlsx.inspect.ndjson'),{force:true});
console.log(`Saved result4.xlsx: ${data.rows.length} records, 21 fixed-distance columns + surface`);
