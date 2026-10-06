'use strict';
const money=n=>new Intl.NumberFormat('en-TH').format(n);
const make=(tag,text,cls)=>{const e=document.createElement(tag);if(text)e.textContent=text;if(cls)e.className=cls;return e;};
Promise.all([fetch('/api/business/catalog').then(r=>r.json()),fetch('/api/business/branches').then(r=>r.json())]).then(([catalog,branches])=>{
 const grid=document.getElementById('home-packages');grid.replaceChildren();
 catalog.packages.slice(0,3).forEach((p,i)=>{const card=make('article',null,'package-card'+(i===1?' featured':''));card.append(make('span',`0${i+1} / HEALTH CHECK`,'package-number'),make('h3',p.name));const price=make('p',`฿${money(p.price_thb)} `,'price');price.append(make('small',p.price_unit));card.append(price);const ul=make('ul');p.services.forEach(t=>ul.append(make('li',t)));card.append(ul);const link=make('a','Explore this health check ↗','button '+(i===1?'primary':'secondary'));link.href='/app?package='+encodeURIComponent(p.id);card.append(link);grid.append(card);});
 const bg=document.getElementById('home-branches');branches.branches.forEach(b=>{const card=make('article',null,'branch-card');card.append(make('div',null,'branch-visual'));const info=make('div');info.append(make('h3',b.name.replace(' Demo','')),make('p',b.area));const a=make('a','Explore this center ↗','text-link');a.href='/app?view=branches';info.append(a);card.append(info);bg.append(card);});
}).catch(()=>{document.getElementById('home-packages').textContent='Health checks are temporarily unavailable. Please try again.';});
if(window.gsap&&!matchMedia('(prefers-reduced-motion: reduce)').matches){gsap.from('.hero-copy > *',{opacity:0,y:20,duration:.7,stagger:.1,ease:'power2.out'});gsap.from('.hero-art',{opacity:0,duration:1.2});}
