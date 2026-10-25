(function(){
var KEY='newgrad-brief-excluded',ex=[];
try{ex=JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){ex=[]}
function save(){try{localStorage.setItem(KEY,JSON.stringify(ex))}catch(e){}}
/* 제외 확정은 아티팩트 db(excluded)에도 저장 → 다음 브리핑에서 빠짐 · 다른 기기에도 반영 */
var DB=null,dbq=Promise.resolve();
function hid(u){var h=5381;for(var i=0;i<u.length;i++){h=((h<<5)+h+u.charCodeAt(i))>>>0}return 'x'+h.toString(36)+'-'+u.length}
function dbw(fn){if(!DB)return;dbq=dbq.then(fn).catch(function(e){if(e&&e.code==='invalid_argument'){DB=null;msg.textContent='이 화면에서는 다음 브리핑 제외를 저장할 수 없습니다 (이 기기에서만 숨김)'}})}
if(window.claude&&claude.use){claude.use('db').then(function(db){if(!db)return;DB=db;
  db.collection('excluded').onSnapshot(function(snap){var seen={};ex.forEach(function(x){seen[x.u]=1});
    snap.docs.forEach(function(d){var v=d.data();if(v&&v.url&&!seen[v.url]){ex.push({u:v.url,c:v.company||'',t:v.title||''});seen[v.url]=1}});
    snap.docChanges().forEach(function(c){if(c.type==='removed'){var u=(c.doc.data()||{}).url;ex=ex.filter(function(x){return x.u!==u})}});
    save();refresh()},function(){})})}
var rows=[].slice.call(document.querySelectorAll('tr[data-url]')),del=document.getElementById('del'),msg=document.getElementById('selmsg');
function sel(){return rows.filter(function(r){return !r.hidden&&r.querySelector('.sel').checked})}
function refresh(){
  rows.forEach(function(r){var gone=ex.some(function(x){return x.u===r.dataset.url});r.hidden=gone;if(gone){r.querySelector('.sel').checked=false}r.classList.toggle('on',r.querySelector('.sel').checked)});
  var n=sel().length;del.disabled=!n;del.textContent=n?('선택 삭제 ('+n+')'):'선택 삭제';
  document.querySelectorAll('section.grp').forEach(function(s){var v=s.querySelectorAll('tr[data-url]:not([hidden])').length;s.querySelector('[data-cnt]').textContent=v+'건';var a=s.querySelector('.all');a.checked=false});
  var t=rows.filter(function(r){return !r.hidden}).length,k=document.getElementById('kv-total');if(k)k.textContent=t;
  var ul=document.getElementById('xitems');ul.innerHTML='';document.getElementById('xcnt').textContent=ex.length;
  document.getElementById('xcnt2').textContent=ex.length;document.getElementById('xopen').hidden=!ex.length;document.getElementById('xall').hidden=ex.length<2;
  ex.forEach(function(x,i){var li=document.createElement('li');li.textContent=x.c+' · '+x.t;var b=document.createElement('button');b.type='button';b.textContent='되돌리기';b.onclick=function(){restore([x.u])};li.appendChild(b);ul.appendChild(li)});
  msg.textContent=n?n+'건 선택됨':'체크한 공고를 이 목록에서 뺍니다';
}
document.addEventListener('change',function(e){
  if(e.target.classList.contains('all')){var s=e.target.closest('section');s.querySelectorAll('tr[data-url]:not([hidden]) .sel').forEach(function(c){c.checked=e.target.checked})}
  if(e.target.matches('.sel,.all')){if(!cfm.hidden)ask(false);refresh()}
});
/* 되돌리기: 목록에 다시 보이고 db에서도 지워져 다음 브리핑에 다시 나온다 */
var last=[],undo=document.getElementById('undo');
function restore(us){ex=ex.filter(function(x){return us.indexOf(x.u)<0});save();
  us.forEach(function(u){dbw(function(){return DB.collection('excluded').doc(hid(u)).delete()})});
  last=last.filter(function(u){return us.indexOf(u)<0});undo.hidden=!last.length;refresh();msg.textContent=us.length+'건 되돌렸습니다'}
undo.onclick=function(){if(last.length)restore(last.slice())};
document.getElementById('xall').onclick=function(){restore(ex.map(function(x){return x.u}))};
document.getElementById('xopen').onclick=function(){var d=document.getElementById('xl');d.open=true;document.getElementById('xsec').scrollIntoView({behavior:'smooth',block:'start'})};
var cfm=document.getElementById('cfm'),yes=document.getElementById('yes');
function ask(on){cfm.hidden=!on;del.hidden=on;if(on){msg.textContent=sel().length+'건을 제외할까요?';yes.focus()}else{del.focus()}}
del.onclick=function(){if(sel().length){undo.hidden=true;ask(true)}};
document.getElementById('no').onclick=function(){ask(false);refresh()};
yes.onclick=function(){var s=sel();last=s.map(function(r){return r.dataset.url});s.forEach(function(r){var x={u:r.dataset.url,c:r.dataset.co,t:r.dataset.title};ex.push(x);
  dbw(function(){return DB.collection('excluded').doc(hid(x.u)).set({url:x.u,company:x.c,title:x.t,at:new Date().toISOString()})})});
  save();ask(false);refresh();undo.hidden=false;undo.focus();msg.textContent=s.length+'건 제외 확정 · 다음 브리핑부터 빠집니다'};
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!cfm.hidden){ask(false);refresh()}});
/* 접수기한 D-n: 오늘 기준으로 다시 계산 (3일 이내 빨간색) */
var t0=new Date();t0.setHours(0,0,0,0);
document.querySelectorAll('td.dl[data-dl]').forEach(function(td){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(td.dataset.dl);if(!m)return;var dd=new Date(+m[1],m[2]-1,+m[3]),n=Math.round((dd-t0)/864e5);
  td.classList.toggle('urgent',n>=0&&n<=3);td.querySelector('.tag').textContent=n<0?'마감':(n===0?'D-day':'D-'+n)});
var tb=document.getElementById('theme');tb.onclick=function(){var r=document.documentElement,d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);r.dataset.theme=d?'light':'dark'};
document.getElementById('print').onclick=function(){window.print()};
refresh();
})();
/* 바로가기 목록에서 행으로 이동하면 잠깐 강조 */
document.addEventListener('click',function(e){var a=e.target.closest('a[href^="#row-"]');if(!a)return;var r=document.querySelector(a.getAttribute('href'));if(r){setTimeout(function(){r.classList.remove('flash');void r.offsetWidth;r.classList.add('flash')},300)}});
