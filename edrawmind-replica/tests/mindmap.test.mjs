import assert from 'node:assert/strict';
import {test} from 'node:test';
import {MindMapDocument} from '../src/mindmap.mjs';

test('新增子主题、兄弟主题并维护树结构',()=>{
 const m=new MindMapDocument({title:'Italiano'}), root=m.root.id;
 const a=m.addChild(root,'Saluti'),b=m.addSibling(a,'Viaggio');
 assert.deepEqual(m.root.children.map(n=>n.text),['Saluti','Viaggio']);
 m.updateNode(a,{text:'Ciao',note:'你好',tags:['A1']});
 assert.equal(m.getNode(a).note,'你好');assert.equal(m.getNode(b).text,'Viaggio');
});
test('节点移动、循环检测和事务回滚',()=>{
 const m=new MindMapDocument(),r=m.root.id,a=m.addChild(r,'A'),b=m.addChild(a,'B'),c=m.addChild(r,'C');
 assert.throws(()=>m.moveNode(a,b),/不能移动/);
 assert.equal(m.getNode(a).children[0].id,b);
 m.moveNode(b,c);assert.equal(m.getNode(c).children[0].id,b);
});
test('删除节点自动清理关系线',()=>{
 const m=new MindMapDocument(),r=m.root.id,a=m.addChild(r,'A'),b=m.addChild(r,'B');
 m.addRelationship(a,b,'关联');assert.equal(m.snapshot().relationships.length,1);
 m.removeNode(a);assert.equal(m.snapshot().relationships.length,0);
 assert.equal(m.getNode(a),null);
});
test('撤销重做与新编辑清空重做栈',()=>{
 const m=new MindMapDocument(),r=m.root.id;
 const a=m.addChild(r,'A');assert.equal(m.undo(),true);assert.equal(m.getNode(a),null);
 assert.equal(m.redo(),true);assert.equal(m.getNode(a).text,'A');
 m.undo();m.addChild(r,'B');assert.equal(m.redo(),false);
});
test('Markdown/JSON 往返与导入层级',()=>{
 const raw='- Italiano\n  - Saluti\n    - Ciao\n  - Viaggio\n';
 const m=MindMapDocument.fromMarkdown(raw);
 assert.equal(m.toMarkdown(),raw);
 const restored=MindMapDocument.fromJSON(m.toJSON());
 assert.deepEqual(restored.snapshot(),m.snapshot());
});
test('非法导入、非法编辑和根保护',()=>{
 assert.throws(()=>MindMapDocument.fromMarkdown('- A\n      - invalid'),/节点层级跳跃/);
 const m=new MindMapDocument();const r=m.root.id;
 assert.throws(()=>m.removeNode(r),/不能删除根/);
 assert.throws(()=>m.setLayout('nonesuch'),/未知布局/);
 assert.equal(m.snapshot().meta.layout,'mindmap');
});
test('任务字段、层级、布局可供看板甘特和演示视图使用',()=>{
 const m=new MindMapDocument(),r=m.root.id,a=m.addChild(r,'Lesson 1');
 m.updateNode(a,{task:{status:'todo',start:'2026-11-13',end:'2026-11-14',progress:0}});
 m.setLayout('timeline');
 assert.equal(m.flatten().find(n=>n.id===a).task.status,'todo');
 assert.equal(m.snapshot().meta.layout,'timeline');
});
