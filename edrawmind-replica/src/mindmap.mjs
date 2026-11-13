// Independent functional mind-map data engine. No proprietary EdrawMind code.
const clone=x=>JSON.parse(JSON.stringify(x));
const uid=()=>globalThis.crypto?.randomUUID?.()||('n'+Math.random().toString(36).slice(2));
export class MindMapDocument {
  constructor(input={title:'新建脑图'}) {
    this.data=clone(input.root?input:{version:1,root:{id:uid(),text:input.title||'新建脑图',children:[]},relationships:[],meta:{layout:'mindmap',theme:'cream'}});
    this.undoStack=[];this.redoStack=[];this.validate();
  }
  static fromJSON(text) {return new MindMapDocument(JSON.parse(text));}
  toJSON() {return JSON.stringify(this.data,null,2);}
  snapshot(){return clone(this.data);}
  get root(){return clone(this.data.root);}
  getNode(id){const entry=this.locate(id);return entry?clone(entry.node):null;}
  locate(id) {
    const walk=(node,parent=null,index=-1)=>{
      if(node.id===id)return {node,parent,index};
      for(let i=0;i<(node.children||[]).length;i++){const x=walk(node.children[i],node,i);if(x)return x;}
      return null;
    };
    return walk(this.data.root);
  }
  validate(){
    const ids=new Set();
    const walk=(n)=>{
      if(!n||typeof n.id!=='string'||!n.id||typeof n.text!=='string')throw Error('无效节点');
      if(ids.has(n.id))throw Error('重复节点 ID');
      ids.add(n.id);
      if(!Array.isArray(n.children))throw Error('children 必须是数组');
      for(const c of n.children)walk(c);
    };
    walk(this.data.root);
    if(!Array.isArray(this.data.relationships))throw Error('relations 格式错误');
    for(const r of this.data.relationships)if(!ids.has(r.from)||!ids.has(r.to)||r.from===r.to)throw Error('无效关系线');
    return true;
  }
  transact(fn){
    const before=this.snapshot();
    try {fn();this.validate();this.undoStack.push(before);if(this.undoStack.length>100)this.undoStack.shift();this.redoStack=[];}
    catch(e){this.data=before;throw e;}
    return this.snapshot();
  }
  addChild(parentId,text='新主题'){
    const id=uid();
    this.transact(()=>{const p=this.locate(parentId);if(!p)throw Error('父节点不存在');p.node.children.push({id,text,children:[]});});
    return id;
  }
  addSibling(id,text='新主题'){
    const siblingId=uid();
    this.transact(()=>{const p=this.locate(id);if(!p?.parent)throw Error('根节点不能添加兄弟');p.parent.children.splice(p.index+1,0,{id:siblingId,text,children:[]});});
    return siblingId;
  }
  updateNode(id,patch){
    this.transact(()=>{const p=this.locate(id);if(!p)throw Error('节点不存在');
      const allowed=['text','note','tags','style','task','collapsed','link','image'];
      for(const k of allowed)if(Object.hasOwn(patch,k))p.node[k]=clone(patch[k]);
    });
  }
  removeNode(id){
    this.transact(()=>{const p=this.locate(id);if(!p?.parent)throw Error('不能删除根节点');
      const removed=new Set();
      const collect=n=>{removed.add(n.id);n.children.forEach(collect);};
      collect(p.node);p.parent.children.splice(p.index,1);
      this.data.relationships=this.data.relationships.filter(r=>!removed.has(r.from)&&!removed.has(r.to));
    });
  }
  moveNode(id,newParentId,index){
    this.transact(()=>{
      const a=this.locate(id),p=this.locate(newParentId);
      if(!a?.parent||!p)throw Error('节点不存在或不允许移动根');
      const contains=(n,target)=>n.id===target||n.children.some(c=>contains(c,target));
      if(contains(a.node,newParentId))throw Error('不能移动到自己的子孙节点');
      a.parent.children.splice(a.index,1);
      const children=p.node.children;
      const dest=index===undefined?children.length:Math.max(0,Math.min(index,children.length));
      children.splice(dest,0,a.node);
    });
  }
  addRelationship(from,to,label=''){
    const id=uid();this.transact(()=>{if(!this.locate(from)||!this.locate(to)||from===to)throw Error('关系线端点无效');this.data.relationships.push({id,from,to,label});});return id;
  }
  removeRelationship(id){this.transact(()=>{const n=this.data.relationships.length;this.data.relationships=this.data.relationships.filter(r=>r.id!==id);if(n===this.data.relationships.length)throw Error('关系线不存在');});}
  setLayout(layout){this.transact(()=>{if(!['mindmap','tree','org','fishbone','timeline','outline'].includes(layout))throw Error('未知布局');this.data.meta.layout=layout;});}
  undo(){if(!this.undoStack.length)return false;this.redoStack.push(this.snapshot());this.data=this.undoStack.pop();return true;}
  redo(){if(!this.redoStack.length)return false;this.undoStack.push(this.snapshot());this.data=this.redoStack.pop();return true;}
  toMarkdown(){
    const out=[];const walk=(n,depth)=>{out.push('  '.repeat(depth)+'- '+n.text.replace(/\n/g,' '));n.children.forEach(c=>walk(c,depth+1));};walk(this.data.root,0);return out.join('\n')+'\n';
  }
  static fromMarkdown(markdown){
    const lines=markdown.split(/\r?\n/).filter(s=>s.trim());
    if(!lines.length)throw Error('Markdown 为空');
    let root=null;const stack=[];
    for(const line of lines){
      const m=line.match(/^(\s*)[-*]\s+(.+)$/);
      if(!m)throw Error('仅支持缩进无序列表');
      if(m[1].includes('\t')||m[1].length%2)throw Error('缩进必须为两个空格');
      const depth=m[1].length/2;
      if(depth>stack.length)throw Error('节点层级跳跃');
      const node={id:uid(),text:m[2].trim(),children:[]};
      if(depth===0){if(root)throw Error('只能有一个根节点');root=node;}
      else{if(!stack[depth-1])throw Error('缺少父节点');stack[depth-1].children.push(node);}
      stack[depth]=node;stack.length=depth+1;
    }
    return new MindMapDocument({version:1,root,relationships:[],meta:{layout:'mindmap',theme:'cream'}});
  }
  flatten(){
    const out=[];const visit=(n,parent=null,depth=0)=>{out.push({id:n.id,text:n.text,parent,depth,task:n.task||null});n.children.forEach(c=>visit(c,n.id,depth+1));};visit(this.data.root);return out;
  }
}
