'use strict';
const fs=require('fs');
const G=require(process.argv[2]+'/src/geom.js');
const rows=JSON.parse(fs.readFileSync(0,'utf8'));
const shape={};
for(const row of rows){
  if(!shape[row.piece])shape[row.piece]=G.prepShape(row.piece,1);
  const s=shape[row.piece];
  const a=G.pose(s,row.ca,row.qa,1), b=G.pose(s,row.cb,row.qb,1);
  process.stdout.write(JSON.stringify({sd:G.sdCores(a,b,Infinity,false)})+'\n');
}
