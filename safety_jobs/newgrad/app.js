(function(){
var KEY='newgrad-brief-excluded',ex=[];
try{ex=JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){ex=[]}
function save(){try{localStorage.setItem(KEY,JSON.stringify(ex))}catch(e){}}
var rows=[].slice.call(document.querySelectorAll('tr[data-url]')),del=document.getElementById('del'),msg=document.getElementById('selmsg');
function sel(){return rows.filter(function(r){return !r.hidden&&r.querySelector('.sel').checked})}
function refresh(){
  rows.forEach(function(r){var gone=ex.some(function(x){return x.u===r.dataset.url});r.hidden=gone;if(gone){r.querySelector('.sel').checked=false}r.classList.toggle('on',r.querySelector('.sel').checked)});
  var n=sel().length;del.disabled=!n;del.textContent=n?('선택 삭제 ('+n+')'):'선택 삭제';
  document.querySelectorAll('section.grp').forEach(function(s){var v=s.querySelectorAll('tr[data-url]:not([hidden])').length;s.querySelector('[data-cnt]').textContent=v+'건';var a=s.querySelector('.all');a.checked=false});
  var t=rows.filter(function(r){return !r.hidden}).length,k=document.getElementById('kv-total');if(k)k.textContent=t;
  var ul=document.getElementById('xitems');ul.innerHTML='';document.getElementById('xcnt').textContent=ex.length;
  ex.forEach(function(x,i){var li=document.createElement('li');li.textContent=x.c+' · '+x.t;var b=document.createElement('button');b.type='button';b.textContent='되돌리기';b.onclick=function(){ex.splice(i,1);save();refresh()};li.appendChild(b);ul.appendChild(li)});
  msg.textContent=n?n+'건 선택됨':'체크한 공고를 이 목록에서 뺍니다';
}
document.addEventListener('change',function(e){
  if(e.target.classList.contains('all')){var s=e.target.closest('section');s.querySelectorAll('tr[data-url]:not([hidden]) .sel').forEach(function(c){c.checked=e.target.checked})}
  if(e.target.matches('.sel,.all')){if(!cfm.hidden)ask(false);refresh()}
});
var cfm=document.getElementById('cfm'),yes=document.getElementById('yes');
function ask(on){cfm.hidden=!on;del.hidden=on;if(on){msg.textContent=sel().length+'건을 제외할까요?';yes.focus()}else{del.focus()}}
del.onclick=function(){if(sel().length)ask(true)};
document.getElementById('no').onclick=function(){ask(false);refresh()};
yes.onclick=function(){var s=sel();s.forEach(function(r){ex.push({u:r.dataset.url,c:r.dataset.co,t:r.dataset.title})});save();ask(false);refresh();msg.textContent=s.length+'건 제외 확정 · 아래에서 되돌릴 수 있습니다'};
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
