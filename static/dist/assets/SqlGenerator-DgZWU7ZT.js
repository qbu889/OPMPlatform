import{Ct as E,E as Y,Et as t,It as P,Lt as p,Mt as B,Pt as _,St as I,Tt as c,V as U,Vt as a,X as G,Xt as V,Yt as C,_ as F,b as J,i as d,m as j,ot as K,rn as R,tn as y,wt as q,xt as s,yt as $}from"./element-plus-yJiVLGHU.js";import{t as X}from"./_plugin-vue_export-helper-B0NXFnpq.js";var W={class:"sql-generator"},Z={class:"stats-panel"},ee={class:"stat-card"},te={class:"stat-number"},ae={class:"stat-card"},se={class:"stat-number"},le={class:"stat-card"},oe={class:"stat-number"},ne={class:"content-wrapper"},re={class:"input-section"},ie={class:"card-header-content"},de={class:"example-buttons"},ue={class:"result-section"},me={class:"card-header-content"},pe={key:0,class:"header-actions"},ce={key:0,class:"empty-result"},ve={key:1,class:"result-content"},_e={class:"sql-output"},fe={class:"sql-code"},Re={key:0,class:"explanation"},ye={class:"explanation-content"},qe={class:"card-header-content"},Te={class:"history-list"},Se=["onClick"],Ae={class:"history-time"},be={class:"history-sql"},Ee={__name:"SqlGenerator",setup(ge){const n=C({databaseType:"mysql",sqlType:"select",tableStructure:"",requirement:"",optimization:!0}),i=C({sql:"",explanation:""}),T=V(!1),f=V([]),l=C({totalGenerated:0,successRate:100,avgTime:0,totalRequests:0,failedRequests:0,totalTime:0});B(()=>{const o=localStorage.getItem("sqlGeneratorHistory");o&&(f.value=JSON.parse(o));const e=localStorage.getItem("sqlGeneratorStats");e&&Object.assign(l,JSON.parse(e))});const A=()=>{localStorage.setItem("sqlGeneratorHistory",JSON.stringify(f.value)),localStorage.setItem("sqlGeneratorStats",JSON.stringify(l))},N=async()=>{if(!n.tableStructure||!n.requirement){d.warning("请填写表结构和需求描述");return}T.value=!0;const o=Date.now();try{const e=await(await fetch("/api/generate-sql",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(n)})).json();if(e.success){i.sql=e.data.sql,i.explanation=e.data.explanation,l.totalGenerated++,l.totalRequests++;const m=((Date.now()-o)/1e3).toFixed(2);l.totalTime+=parseFloat(m),l.avgTime=(l.totalTime/l.totalRequests).toFixed(2),l.successRate=((l.totalRequests-l.failedRequests)/l.totalRequests*100).toFixed(1),f.value.unshift({time:new Date().toLocaleString(),sql:e.data.sql,explanation:e.data.explanation,duration:m}),f.value.length>20&&f.value.pop(),A(),d.success("SQL 生成成功")}else l.failedRequests++,l.totalRequests++,l.successRate=((l.totalRequests-l.failedRequests)/l.totalRequests*100).toFixed(1),A(),d.error(e.message||"生成失败")}catch(e){l.failedRequests++,l.totalRequests++,l.successRate=((l.totalRequests-l.failedRequests)/l.totalRequests*100).toFixed(1),A(),d.error("网络错误: "+e.message)}finally{T.value=!1}},k=()=>{navigator.clipboard.writeText(i.sql),d.success("SQL 已复制到剪贴板")},Q=async()=>{if(i.sql)try{const o=await(await fetch("/api/optimize-sql",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sql:i.sql,table_structure:n.tableStructure,database_type:n.databaseType})})).json();o.success&&(i.sql=o.data.optimized_sql,d.success("SQL 优化成功"))}catch(o){d.error("优化失败: "+o.message)}},w=async()=>{if(i.sql)try{const o=await(await fetch("/api/explain-sql",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sql:i.sql,database_type:n.databaseType})})).json();o.success&&(i.explanation=o.data.explanation,d.success("SQL 解释成功"))}catch(o){d.error("解释失败: "+o.message)}},b=o=>{const e={1:{tableStructure:`CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);`,requirement:"查询所有年龄大于 18 岁的用户,按创建时间倒序排列"},2:{tableStructure:`CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100)
);`,requirement:"关联订单表和用户表,查询每个用户的订单总金额,只显示有订单的用户"},3:{tableStructure:`CREATE TABLE sales (
    id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    amount DECIMAL(10,2),
    sale_date DATE
);`,requirement:"统计每个类别的销售总额和平均销售额,按销售总额降序排列"},4:{tableStructure:`CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    department_id INT,
    salary DECIMAL(10,2),
    hire_date DATE
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    location VARCHAR(100)
);`,requirement:"查询每个部门薪资排名前 3 的员工,显示部门名称、员工姓名和薪资"}}[o];e&&(n.tableStructure=e.tableStructure,n.requirement=e.requirement,d.success("已加载示例"))},M=o=>{i.sql=o.sql,i.explanation=o.explanation,d.success("已加载历史记录")},h=()=>{f.value=[],A(),d.success("历史记录已清空")};return(o,e)=>{const m=p("el-icon"),u=p("el-option"),L=p("el-select"),S=p("el-form-item"),x=p("el-input"),H=p("el-checkbox"),v=p("el-button"),z=p("el-form"),g=p("el-card"),D=p("el-empty");return _(),q("div",W,[e[25]||(e[25]=s("div",{class:"page-header"},[s("h1",null," SQL 智能生成器"),s("p",{class:"subtitle"},"基于 AI 的智能 SQL 生成工具,支持复杂查询、多表关联、性能优化")],-1)),s("div",Z,[s("div",ee,[s("div",te,R(l.totalGenerated),1),e[9]||(e[9]=s("div",{class:"stat-label"},"已生成 SQL",-1))]),s("div",ae,[s("div",se,R(l.successRate)+"%",1),e[10]||(e[10]=s("div",{class:"stat-label"},"成功率",-1))]),s("div",le,[s("div",oe,R(l.avgTime||"-"),1),e[11]||(e[11]=s("div",{class:"stat-label"},"平均耗时",-1))])]),s("div",ne,[s("div",re,[t(g,{class:"section-card"},{header:a(()=>[s("div",ie,[t(m,null,{default:a(()=>[t(y(Y))]),_:1}),e[12]||(e[12]=s("span",null,"📋 输入信息",-1))])]),default:a(()=>[t(z,{"label-position":"top"},{default:a(()=>[t(S,{label:"🗄️ 数据库类型"},{default:a(()=>[t(L,{modelValue:n.databaseType,"onUpdate:modelValue":e[0]||(e[0]=r=>n.databaseType=r),style:{width:"100%"}},{default:a(()=>[t(u,{label:"MySQL",value:"mysql"}),t(u,{label:"PostgreSQL",value:"postgresql"}),t(u,{label:"Oracle",value:"oracle"}),t(u,{label:"SQL Server",value:"sqlserver"}),t(u,{label:"SQLite",value:"sqlite"}),t(u,{label:"达梦数据库(DM)",value:"dameng"})]),_:1},8,["modelValue"])]),_:1}),t(S,{label:"📝 SQL 类型"},{default:a(()=>[t(L,{modelValue:n.sqlType,"onUpdate:modelValue":e[1]||(e[1]=r=>n.sqlType=r),style:{width:"100%"}},{default:a(()=>[t(u,{label:"SELECT（查询）",value:"select"}),t(u,{label:"INSERT（插入）",value:"insert"}),t(u,{label:"UPDATE（更新）",value:"update"}),t(u,{label:"DELETE（删除）",value:"delete"}),t(u,{label:"CREATE（创建表）",value:"create"})]),_:1},8,["modelValue"])]),_:1}),t(S,{label:"📊 表结构信息"},{default:a(()=>[t(x,{modelValue:n.tableStructure,"onUpdate:modelValue":e[2]||(e[2]=r=>n.tableStructure=r),type:"textarea",rows:8,placeholder:`请输入表结构信息,支持以下格式:

1. SQL CREATE 语句:
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

2. JSON 格式:
{
  "table": "users",
  "columns": [
    {"name": "id", "type": "INT"},
    {"name": "name", "type": "VARCHAR(50)"}
  ]
}

3. 文本描述:
表名: users
字段:
- id (INT, 主键)
- name (VARCHAR(50))
- age (INT)`},null,8,["modelValue"])]),_:1}),t(S,{label:"💡 需求描述"},{default:a(()=>[t(x,{modelValue:n.requirement,"onUpdate:modelValue":e[3]||(e[3]=r=>n.requirement=r),type:"textarea",rows:4,placeholder:`请描述您需要的 SQL 功能,例如:
- 查询所有年龄大于 18 岁的用户
- 统计每个部门的员工数量
- 关联订单表和用户表,查询用户的订单信息`},null,8,["modelValue"])]),_:1}),t(S,null,{default:a(()=>[t(H,{modelValue:n.optimization,"onUpdate:modelValue":e[4]||(e[4]=r=>n.optimization=r)},{default:a(()=>[...e[13]||(e[13]=[c("启用 SQL 优化建议",-1)])]),_:1},8,["modelValue"])]),_:1}),s("div",de,[t(v,{size:"small",onClick:e[5]||(e[5]=r=>b(1))},{default:a(()=>[...e[14]||(e[14]=[c("示例 1: 基础查询",-1)])]),_:1}),t(v,{size:"small",onClick:e[6]||(e[6]=r=>b(2))},{default:a(()=>[...e[15]||(e[15]=[c("示例 2: 多表关联",-1)])]),_:1}),t(v,{size:"small",onClick:e[7]||(e[7]=r=>b(3))},{default:a(()=>[...e[16]||(e[16]=[c("示例 3: 聚合统计",-1)])]),_:1}),t(v,{size:"small",onClick:e[8]||(e[8]=r=>b(4))},{default:a(()=>[...e[17]||(e[17]=[c("示例 4: 复杂查询",-1)])]),_:1})]),t(S,{style:{"margin-top":"20px"}},{default:a(()=>[t(v,{type:"primary",size:"large",onClick:N,loading:T.value,style:{width:"100%",height:"48px","font-size":"16px"}},{default:a(()=>[T.value?E("",!0):(_(),I(m,{key:0},{default:a(()=>[t(y(U))]),_:1})),c(" "+R(T.value?"生成中...":"生成 SQL"),1)]),_:1},8,["loading"])]),_:1})]),_:1})]),_:1})]),s("div",ue,[t(g,{class:"section-card"},{header:a(()=>[s("div",me,[t(m,null,{default:a(()=>[t(y(j))]),_:1}),e[21]||(e[21]=s("span",null,"✅ 生成结果",-1)),i.sql?(_(),q("div",pe,[t(v,{size:"small",onClick:k},{default:a(()=>[t(m,null,{default:a(()=>[t(y(J))]),_:1}),e[18]||(e[18]=c(" 复制 SQL ",-1))]),_:1}),t(v,{size:"small",onClick:Q},{default:a(()=>[t(m,null,{default:a(()=>[t(y(K))]),_:1}),e[19]||(e[19]=c(" 优化 SQL ",-1))]),_:1}),t(v,{size:"small",onClick:w},{default:a(()=>[t(m,null,{default:a(()=>[t(y(G))]),_:1}),e[20]||(e[20]=c(" 解释 SQL ",-1))]),_:1})])):E("",!0)])]),default:a(()=>[!i.sql&&!T.value?(_(),q("div",ce,[t(D,{description:"输入表结构和需求,点击生成 SQL"})])):(_(),q("div",ve,[s("div",_e,[s("div",fe,R(i.sql),1)]),i.explanation?(_(),q("div",Re,[e[22]||(e[22]=s("div",{class:"explanation-title"},"📖 SQL 说明",-1)),s("div",ye,R(i.explanation),1)])):E("",!0)]))]),_:1}),f.value.length>0?(_(),I(g,{key:0,class:"section-card history-card"},{header:a(()=>[s("div",qe,[t(m,null,{default:a(()=>[t(y(F))]),_:1}),e[24]||(e[24]=s("span",null,"📜 历史记录",-1)),t(v,{size:"small",type:"danger",onClick:h},{default:a(()=>[...e[23]||(e[23]=[c("清空",-1)])]),_:1})])]),default:a(()=>[s("div",Te,[(_(!0),q($,null,P(f.value,(r,O)=>(_(),q("div",{key:O,class:"history-item",onClick:Ce=>M(r)},[s("div",Ae,R(r.time),1),s("div",be,R(r.sql.substring(0,50))+"...",1)],8,Se))),128))])]),_:1})):E("",!0)])])])}}},Ie=X(Ee,[["__scopeId","data-v-be8eabdb"]]);export{Ie as default};
