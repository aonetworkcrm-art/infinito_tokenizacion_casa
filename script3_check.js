
var MAX_BALANCE = 100000;
var staked = 0;
var whaleInterval = null;
var clockInterval = null;

// ─── NOTIFICATION ───
function showNotif(msg, color) {
  var n = document.getElementById("notif");
  n.textContent = msg;
  n.style.borderColor = color || "var(--border)";
  n.style.color = color || "var(--grn)";
  n.className = "show";
  setTimeout(function(){ n.className = ""; }, 3000);
}



// ─── TAB SYSTEM ───
function switchTab(tabId){
document.querySelectorAll(".tab").forEach(function(t){t.classList.remove("act")});
document.querySelectorAll(".tc").forEach(function(t){t.classList.remove("act")});
document.querySelector(".tab[data-tab='"+tabId+"']").classList.add("act");
document.getElementById(tabId).classList.add("act");
}
function initTabs(){
document.querySelectorAll(".tab").forEach(function(tab){
tab.addEventListener("click",function(){switchTab(this.dataset.tab)});
});
}
if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',initTabs)}else{initTabs()}

// ─── SHADOW SILO SEEDS ───
document.getElementById("shadow-posts").textContent = "5";
document.getElementById("shadow-keywords").textContent = "12";
document.getElementById("shadow-traffic").textContent = "7,000";
document.getElementById("shadow-yield").textContent = "$8,190.00";

// ─── DASHBOARD ANIMATION (Unificada) ───
function animateDashboard(){
var targets=[
{el:"hdr-tokens",val:1000000,fmt:function(v){return v.toLocaleString()+" TI"}},
{el:"hdr-whales",val:99,fmt:function(v){return v}},
{el:"hdr-value",val:103000,fmt:function(v){return "$"+v.toLocaleString()}},
{el:"dash-treasury",val:42600,fmt:function(v){return "$"+v.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}},
{el:"dash-monthly",val:293150,fmt:function(v){return "$"+v.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}}
];
var progress = targets.map(function(){return 0});
var step = 1;
function tick(){
var done = 0;
for(var i=0;i<targets.length;i++){
if(progress[i] >= targets[i].val){
done++;
continue;
}
progress[i] = Math.min(progress[i] + Math.ceil(targets[i].val/60), targets[i].val);
var el = document.getElementById(targets[i].el);
if(el) el.textContent = targets[i].fmt(progress[i]);
}
if(done < targets.length) requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
}
animateDashboard();

// ─── MEMPOOL SIMULATION ───
var mempoolTX = [];
var mempoolBlock = 0;
var mempoolBaseTime = Date.now();

function genHash(){var h="0x";for(var i=0;i<40;i++)h+="0123456789abcdef"[Math.floor(Math.random()*16)];return h.slice(0,10)+"..."+h.slice(-4)}
function genAddr(){var a="0x";for(var i=0;i<40;i++)a+="0123456789abcdef"[Math.floor(Math.random()*16)];return a.slice(0,6)+"..."+a.slice(-4)}

var txTypes=[
{name:"Juvenil",emoji:"",min:5000,max:50000,color:"lo"},
{name:"Azul",emoji:"",min:50000,max:250000,color:"md"},
{name:"Dorada",emoji:"✨",min:250000,max:1000000,color:"hi"},
{name:"Mítica",emoji:"💎",min:1000000,max:5000000,color:"mega"}
];

function generateTX(){
var type=txTypes[Math.floor(Math.random()*txTypes.length)];
var val=Math.floor(type.min+Math.random()*(type.max-type.min));
var gas=Math.floor(30+Math.random()*200);
var conf=Math.random();
return{
type:type.name,
emoji:type.emoji,
val:val,
gas:gas,
from:genAddr(),
to:genAddr(),
hash:genHash(),
time:Date.now(),
conf:conf,
color:type.color
};
}

function initMempool(){
var feed=document.getElementById("mp-feed");
if(!feed)return;
var head=feed.querySelector(".mp-row-head");
feed.innerHTML="";
if(head)feed.appendChild(head);
mempoolTX=[];
for(var i=0;i<18;i++){
mempoolTX.push(generateTX());
}
mempoolBlock=Math.floor(Math.random()*9000000+1000000);
renderMempool();
updateMempoolStats();
updateTopWhales();
}

function renderMempool(){
var feed=document.getElementById("mp-feed");
if(!feed)return;
var head=feed.querySelector(".mp-row-head");
feed.innerHTML="";
if(head)feed.appendChild(head);

// Sort by value descending
var sorted=mempoolTX.slice().sort(function(a,b){return b.val-a.val});

for(var i=0;i<sorted.length;i++){
var tx=sorted[i];
var row=document.createElement("div");
row.className="mp-row";
if(i<3)row.classList.add("mp-row-new");

var valClass="mp-val-"+tx.color;
var confPct=(tx.conf*100).toFixed(0);
var confColor=tx.conf>0.7?"var(--grn)":tx.conf>0.4?"var(--go)":"var(--rd)";
var age=Math.floor((Date.now()-tx.time)/1000);
var timeStr=age<60?age+"s":Math.floor(age/60)+"m";

row.innerHTML=
"<span>"+tx.emoji+"</span>"+
"<span style='color:"+confColor+"'>"+tx.type+"</span>"+
"<span class='mp-val "+valClass+"'>$"+tx.val.toLocaleString()+"</span>"+
"<span class='mp-gas'>"+tx.gas+" Gwei</span>"+
"<span class='mp-addr'>"+tx.from+"</span>"+
"<span class='mp-addr'>"+tx.to+"</span>"+
"<span class='mp-conf' style='color:"+confColor+"'>"+confPct+"%</span>";
feed.appendChild(row);
}
}

function updateMempoolStats(){
var totalVal=0;
var whales=0;
var totalGas=0;
for(var i=0;i<mempoolTX.length;i++){
totalVal+=mempoolTX[i].val;
if(mempoolTX[i].val>100000)whales++;
totalGas+=mempoolTX[i].gas;
}
var avgGas=mempoolTX.length>0?Math.floor(totalGas/mempoolTX.length):0;

document.getElementById("mp-total-val").textContent="$"+totalVal.toLocaleString();
document.getElementById("mp-tx-count").textContent=mempoolTX.length;
document.getElementById("mp-gas-avg").textContent=avgGas;
document.getElementById("mp-whale-count").textContent=whales;
}

function updateTopWhales(){
var list=document.getElementById("mp-top-list");
if(!list)return;
var sorted=mempoolTX.slice().sort(function(a,b){return b.val-a.val});
var top3=sorted.slice(0,3);
var html="";
var ranks=["🥇","🥈","🥉"];
for(var i=0;i<top3.length;i++){
var tx=top3[i];
var valClass="mp-val-"+tx.color;
var age=Math.floor((Date.now()-tx.time)/1000);
var timeStr=age<60?age+"s":Math.floor(age/60)+"m";
html+="<div style='display:flex;justify-content:space-between;align-items:center;padding:8px 14px;border-bottom:1px solid rgba(255,255,255,0.04);font-size:10px'>"+
"<span>"+ranks[i]+" "+tx.emoji+" <span style='color:var(--cy);font-weight:600'>"+tx.type+"</span></span>"+
"<span class='"+valClass+"' style='font-weight:700'>$"+tx.val.toLocaleString()+"</span>"+
"<span class='mp-gas'>"+tx.gas+" Gwei</span>"+
"<span class='mp-addr'>"+tx.from+" &rarr; "+tx.to+"</span>"+
"<span style='color:var(--dim);font-size:8px'>"+timeStr+" atr&aacute;s</span>"+
"</div>";
}
list.innerHTML=html;
}

function updateAlerts(){
var sorted=mempoolTX.slice().sort(function(a,b){return b.val-a.val});
var top=sorted[0];
var titleEl=document.getElementById("mp-alert-title");
var descEl=document.getElementById("mp-alert-desc");
var valEl=document.getElementById("mp-alert-val");
if(!titleEl)return;

if(top.val>=1000000){
titleEl.textContent="🚨 ¡Ballena Mítica Detectada!";
descEl.textContent="Transacci\u00f3n de m\u00e1s de $1M USD detectada en el mempool. Preparando arbitraje Flash Loan...";
valEl.textContent="$"+top.val.toLocaleString();
document.getElementById("mp-alert-box").style.borderColor="rgba(220,38,38,0.4)";
} else if(top.val>=250000){
titleEl.textContent="🐋 Ballena Dorada en el Radar";
descEl.textContent="Transacci\u00f3n de alto valor detectada. Evaluando oportunidad de extracci\u00f3n MEV.";
valEl.textContent="$"+top.val.toLocaleString();
document.getElementById("mp-alert-box").style.borderColor="rgba(245,158,11,0.3)";
} else {
titleEl.textContent="✅ Monitoreando Mempool";
descEl.textContent="El sistema escanea 24/7. Esperando ballenas de alto valor para cazar.";
valEl.textContent="";
document.getElementById("mp-alert-box").style.borderColor="rgba(45,138,78,0.2)";
}
}

function simulateMempool(){
// Add 2-4 new transactions
var newCount=1+Math.floor(Math.random()*3);
for(var i=0;i<newCount;i++){
mempoolTX.push(generateTX());
}
// Remove some old ones (simulating blocks clearing)
if(mempoolTX.length>25){
mempoolTX.sort(function(a,b){return a.time-b.time});
mempoolTX=mempoolTX.slice(-22);
}
mempoolBlock++;
document.getElementById("mp-block-info").textContent="Bloque #"+mempoolBlock;

renderMempool();
updateMempoolStats();
updateTopWhales();
updateAlerts();
}

initMempool();
simulateMempool();

// ─── PAGE VISIBILITY API ───
function startIntervals(){
if(!whaleInterval) whaleInterval = setInterval(simulateMempool, 8000);
if(!clockInterval) clockInterval = setInterval(updateClock, 1000);
}
function stopIntervals(){
if(whaleInterval){clearInterval(whaleInterval);whaleInterval=null;}
if(clockInterval){clearInterval(clockInterval);clockInterval=null;}
}
document.addEventListener("visibilitychange", function(){
if(document.hidden){ stopIntervals(); }
else { startIntervals(); }
});
startIntervals();

// ─── STAKING (Corregido) ───
function stakeTokens(){
var inp = document.getElementById("stake-amount");
var amt = parseInt(inp.value);
if(!amt||amt<=0){ showNotif("❌ Ingresa una cantidad v\u00e1lida de TI","var(--rd)"); return; }
if(staked+amt > MAX_BALANCE){ showNotif("❌ No tienes suficientes TI. M\u00e1ximo: "+(MAX_BALANCE-staked)+" TI","var(--rd)"); return; }
staked += amt;
document.getElementById("stake-balance").textContent = (MAX_BALANCE-staked).toLocaleString()+" TI";
document.getElementById("stake-locked").textContent = staked.toLocaleString()+" TI";
inp.value = "";
document.querySelectorAll(".dc-lock-overlay").forEach(function(o){o.style.display="none"});
document.querySelectorAll(".dc-lock").forEach(function(c){c.style.opacity="1";c.style.filter="none";c.style.pointerEvents="auto"});
showNotif("✅ Stakeado exitosamente! "+amt.toLocaleString()+" TI bloqueados","var(--grn)");
}
function unstakeTokens(){
if(staked<=0){ showNotif("❌ No tienes tokens stakados","var(--rd)"); return; }
var inp = document.getElementById("stake-amount");
var amt = parseInt(inp.value);
if(!amt||amt<=0){ showNotif("❌ Ingresa cu\u00e1ntos TI unstakear","var(--rd)"); return; }
if(amt > staked){ showNotif("❌ Solo tienes "+staked.toLocaleString()+" TI stakados","var(--rd)"); return; }
staked -= amt;
document.getElementById("stake-balance").textContent = (MAX_BALANCE-staked).toLocaleString()+" TI";
document.getElementById("stake-locked").textContent = staked.toLocaleString()+" TI";
inp.value = "";
if(staked <= 0){
document.querySelectorAll(".dc-lock-overlay").forEach(function(o){o.style.display="flex"});
document.querySelectorAll(".dc-lock").forEach(function(c){c.style.opacity="0.5";c.style.filter="blur(2px)";c.style.pointerEvents="none"});
}
showNotif("✅ "+amt.toLocaleString()+" TI unstakados","var(--grn)");
}

// ─── VOTING ───
function vote(propId, isYes){
var bar = document.getElementById(propId+"-bar");
var yesLabel = document.getElementById(propId+"-yes");
var noLabel = document.getElementById(propId+"-no");
var status = document.getElementById(propId+"-status");
var w = parseFloat(bar.style.width) || 0;
if(isYes){
var newW = Math.min(w + 5, 100);
bar.style.width = newW + "%";
yesLabel.textContent = "👍 "+newW.toFixed(0)+"% a favor";
noLabel.textContent = "👎 "+(100-newW).toFixed(0)+"% en contra";
status.innerHTML = "<span class='dot'></span> En Votaci\u00f3n";
status.className = "bg bg-gr";
showNotif("🗳️ Voto registrado: S\u00ed ("+newW.toFixed(0)+"%)","var(--cy)");
} else {
var newW = Math.min(w + 5, 100);
bar.style.width = (100-newW) + "%";
yesLabel.textContent = "👍 "+(100-newW).toFixed(0)+"% a favor";
noLabel.textContent = "👎 "+newW.toFixed(0)+"% en contra";
status.innerHTML = "<span class='dot'></span> En Votaci\u00f3n";
status.className = "bg bg-gr";
showNotif("🗳️ Voto registrado: No ("+newW.toFixed(0)+"%)","var(--rd)");
}
}

// ─── WALLET ───
async function connectWallet(){
if(typeof window.ethereum==="undefined"){
document.getElementById("wallet-status").innerHTML = "<span style='color:var(--rd)'>MetaMask no instalado. <a href='https://metamask.io' target='_blank' style='color:var(--cy)'>Instalar</a></span>";
return;
}
document.getElementById("wallet-status").textContent = "Conectando...";
try {
var accounts = await window.ethereum.request({method:"eth_requestAccounts"});
var addr = accounts[0];

// Configurar provider ethers.js
var provider = new ethers.BrowserProvider(window.ethereum);
var signer = await provider.getSigner();
var network = await provider.getNetwork();
var networkName = network.name==="matic"||network.chainId===80002?"Polygon (Amoy Testnet)":"Chain ID: "+network.chainId;
var balanceMatic = await provider.getBalance(addr);
var maticFormatted = ethers.formatEther(balanceMatic);

// Inicializar contrato TI
var contractReady = await initContract(provider, signer);
var tiBalance = "0";
var tiFormatted = "0 TI";
var divsFormatted = "$0.00";

if(contractReady && tiContract){
try {
var rawBal = await tiContract.balanceOf(addr);
tiBalance = ethers.formatEther(rawBal);
tiFormatted = parseFloat(tiBalance).toLocaleString(undefined,{maximumFractionDigits:2})+" TI";
// Dividendos simulados hasta implementar DividendDistributor
var divsAmount = (parseFloat(tiBalance) * 0.02 * Math.random() * 0.1).toFixed(2);
divsFormatted = "$"+divsAmount;
} catch(e) {
console.warn("⚠️ Could not fetch TI balance:",e.message);
tiFormatted = "⚠️ Sin contrato";
}
} else {
tiFormatted = "⚠️ No deployado";
}

document.getElementById("wallet-address").textContent = addr;
document.getElementById("wallet-address").style.display = "block";
document.getElementById("wallet-status").textContent = "Conectado: "+addr.slice(0,6)+"..."+addr.slice(-4);
document.getElementById("wallet-btn").textContent = "Cambiar Wallet";
document.getElementById("wallet-disconnect").style.display = "inline-block";
document.getElementById("wallet-info").style.display = "block";
document.getElementById("wallet-network").textContent = networkName;
document.getElementById("wallet-matic").textContent = parseFloat(maticFormatted).toFixed(4)+" MATIC";
document.getElementById("wallet-ti").textContent = tiFormatted;
document.getElementById("wallet-divs").textContent = divsFormatted;
showNotif("🦊 Wallet conectada exitosamente","var(--cy)");
} catch(err) {
console.error("Wallet connection error:",err);
document.getElementById("wallet-status").innerHTML = "<span style='color:var(--rd)'>Conexi\u00f3n rechazada: "+err.message+"</span>";
}
}
function disconnectWallet(){
document.getElementById("wallet-address").style.display = "none";
document.getElementById("wallet-status").textContent = "No conectado";
document.getElementById("wallet-btn").textContent = "Conectar MetaMask";
document.getElementById("wallet-disconnect").style.display = "none";
document.getElementById("wallet-info").style.display = "none";
tiContract = null;
}

// ─── CLOCK ───
function updateClock(){
var d = new Date();
var opts = {year:"numeric",month:"long",day:"numeric",hour:"2-digit",minute:"2-digit",second:"2-digit"};
var el = document.querySelector(".hdr-sub");
if(el) el.textContent = d.toLocaleDateString("es-ES",opts)+"  |  Polygon Amoy Testnet";
}

// ─── IN-FINITY RAIN (Letras de INFINITO cayendo) ───
(function(){
var c=document.getElementById("infinitoCanvas");
if(!c)return;
var ctx=c.getContext("2d");
var W,H;
function resize(){W=c.width=innerWidth;H=c.height=innerHeight}
resize();window.onresize=resize;
var letters="INFINITO";
var fontSize=14;
var cols=Math.floor(W/(fontSize*0.8));
var drops=[];
for(var i=0;i<cols;i++){
drops[i]=Math.random()*-120;
}
var grn="#2d8a4e";
var cy="#0891b2";
function draw(){
ctx.fillStyle="rgba(15,10,6,0.06)";
ctx.fillRect(0,0,W,H);
for(var i=0;i<drops.length;i++){
var text=letters[Math.floor(Math.random()*letters.length)];
var x=i*(fontSize*0.8);
var y=drops[i]*fontSize*1.2;
if(y>0&&y<H){
var alpha=Math.min(1,0.3+Math.random()*0.7);
var useCyan=Math.random()>0.85;
ctx.fillStyle=useCyan?cy:grn;
ctx.globalAlpha=alpha;
ctx.font=fontSize+"px monospace";
ctx.fillText(text,x,y);
ctx.globalAlpha=1;
}
drops[i]+=0.3+Math.random()*0.6;
if(y>H+50&&Math.random()>0.98)drops[i]=Math.random()*-60;
}
requestAnimationFrame(draw);
}
draw();
})();

// ─── FAMILY WALLETS CONFIG ───
function renderFamilyWallets(){
var grid=document.getElementById("wallet-config-grid");
if(!grid)return;
var html="";
var saved=JSON.parse(localStorage.getItem("infinito_wallets")||"{}");
for(var key in FAMILY_WALLETS){
var w=FAMILY_WALLETS[key];
var addr=saved[key]||w.address||"";
html+="<div style='display:flex;flex-direction:column;gap:4px;padding:8px;border:1px solid var(--border)'>"+
"<span style='font-size:10px;color:var(--cy)'>"+w.name+"</span>"+
"<input class='inp wallet-input' data-key='"+key+"' type='text' value='"+addr+"' placeholder='0x...' style='font-size:9px;font-family:monospace'>"+
"<span style='font-size:8px;color:var(--dim)' id='wallet-status-"+key+"'></span></div>";
}
grid.innerHTML=html;
}
function saveFamilyWallets(){
var wallets={};
document.querySelectorAll(".wallet-input").forEach(function(inp){
var key=inp.dataset.key;
var val=inp.value.trim();
if(val)wallets[key]=val;
});
localStorage.setItem("infinito_wallets",JSON.stringify(wallets));
showNotif("💾 Wallets guardadas localmente ("+Object.keys(wallets).length+" direcciones)","var(--grn)");
}
renderFamilyWallets();

// ─── TUNNEL URL CONFIG ───
var tunnelURL = localStorage.getItem("infinito_tunnel_url") || "";

function toggleTunnelConfig(){
  var form = document.getElementById("tunnel-config-form");
  if(!form) return;
  form.style.display = form.style.display==="none"?"block":"none";
  if(form.style.display==="block"){
    var inp = document.getElementById("tunnel-url-input");
    if(inp) inp.value = tunnelURL;
  }
}

function saveTunnelURL(){
  var inp = document.getElementById("tunnel-url-input");
  if(!inp) return;
  tunnelURL = inp.value.trim();
  localStorage.setItem("infinito_tunnel_url", tunnelURL);
  updateTunnelDisplay();
  showNotif("🌐 Endpoint API actualizado: "+(tunnelURL || "localhost:8000"),"var(--cy)");
}

function applyAPIPreset(preset){
  var inp = document.getElementById("tunnel-url-input");
  if(!inp) return;
  var urls = {
    "localhost": "http://localhost:8000",
    "render": "https://proyecto-infinito-api.onrender.com",
    "vercel": "https://proyecto-infinito-api.vercel.app",
    "cloudflare": "https://infinito-api.trycloudflare.com",
  };
  if(urls[preset]){
    inp.value = urls[preset];
  }
}

function updateTunnelDisplay(){
  var el = document.getElementById("tunnel-current");
  if(el) el.textContent = tunnelURL || "localhost:8000";
  // Update API_ENDPOINTS
  API_ENDPOINTS.length = 0;
  API_ENDPOINTS.push("http://localhost:8000");
  if(tunnelURL) API_ENDPOINTS.push(tunnelURL);
}

// Restore tunnel URL display on load
(function(){
  var el = document.getElementById("tunnel-current");
  if(el) el.textContent = tunnelURL || "localhost:8000";
})();

// ─── SHADOW SILO — GENERATE NEXT POST ───
var generatedPosts = JSON.parse(localStorage.getItem("infinito_shadow_posts")||"[]");

// SEO Oracle niches data embebido (fuente de verdad para generación)
var SHADOW_NICHES = [
  {id:"personal-injury-law",name:"Abogados de Accidentes",cat:"Servicios Legales",cpc_min:150,cpc_max:300,cpc_avg:220,vol:"muy_alto",dificultad:"muy_alta",evergreen:10,intent:"transaccional",kw:["car accident lawyer near me","personal injury attorney","truck accident lawyer","abogado de accidentes","mesothelioma law firm"]},
  {id:"asset-recovery",name:"Recuperación de Activos",cat:"Servicios Legales",cpc_min:100,cpc_max:150,cpc_avg:125,vol:"medio",dificultad:"alta",evergreen:9,intent:"transaccional",kw:["asset recovery services","recuperar fondos estafados","fund recovery specialist","tracing crypto legal","stolen asset recovery"]},
  {id:"cybersecurity-compliance",name:"Ciberseguridad y Compliance",cat:"Tecnología B2B",cpc_min:140,cpc_max:200,cpc_avg:170,vol:"medio",dificultad:"alta",evergreen:9,intent:"comercial",kw:["SOC 2 compliance certification","enterprise cybersecurity","penetration testing services","managed security provider","cybersecurity audit firm"]},
  {id:"drug-rehab",name:"Centros de Rehabilitación",cat:"Salud",cpc_min:80,cpc_max:150,cpc_avg:120,vol:"muy_alto",dificultad:"muy_alta",evergreen:10,intent:"transaccional",kw:["inpatient drug rehab centers","alcohol rehabilitation near me","centro de rehabilitación","luxury rehab facility","detox center"]},
  {id:"life-insurance-seniors",name:"Seguros de Vida para Adultos Mayores",cat:"Seguros",cpc_min:70,cpc_max:120,cpc_avg:95,vol:"muy_alto",dificultad:"alta",evergreen:9,intent:"comercial",kw:["life insurance for seniors over 70","best life insurance seniors","final expense insurance","burial insurance","seguro de vida adultos mayores"]},
  {id:"online-mba",name:"MBA y Posgrados Online",cat:"Educación",cpc_min:70,cpc_max:130,cpc_avg:100,vol:"alto",dificultad:"media",evergreen:8,intent:"comercial",kw:["online MBA for working professionals","best executive MBA online","accredited online master degree","maestría en línea","online finance degree"]},
  {id:"high-risk-auto",name:"Seguros de Auto Alto Riesgo",cat:"Seguros",cpc_min:80,cpc_max:130,cpc_avg:105,vol:"muy_alto",dificultad:"alta",evergreen:9,intent:"transaccional",kw:["high risk auto insurance","SR22 insurance","non owner car insurance","cheap auto insurance after accident","suspended license insurance"]},
  {id:"defi-investment",name:"Inversiones y Gestión DeFi",cat:"Finanzas",cpc_min:60,cpc_max:110,cpc_avg:85,vol:"medio",dificultad:"media",evergreen:7,intent:"comercial",kw:["DeFi asset management","yield farming strategies 2026","best crypto investment platform","inversiones criptomonedas","crypto portfolio management"]},
  {id:"mesothelioma",name:"Mesotelioma y Enf. Laborales",cat:"Servicios Legales",cpc_min:100,cpc_max:200,cpc_avg:150,vol:"bajo",dificultad:"muy_alta",evergreen:10,intent:"transaccional",kw:["mesothelioma law firm","mesothelioma compensation","asbestos cancer lawyer","compensación mesotelioma","lung cancer attorney"]},
  {id:"enterprise-cyber",name:"Ciberseguridad Empresarial",cat:"Tecnología B2B",cpc_min:90,cpc_max:160,cpc_avg:120,vol:"alto",dificultad:"alta",evergreen:9,intent:"comercial",kw:["enterprise cybersecurity solutions","managed detection response","cloud security business","zero trust security","ransomware protection"]}
];

var API_ENDPOINTS = [
  "http://localhost:8000",
];

// Add tunnel URL if configured
if(typeof tunnelURL !== 'undefined' && tunnelURL) {
  API_ENDPOINTS.push(tunnelURL);
}

function generateNextPost(){
  // Find the button by its onclick context
  var btns = document.querySelectorAll(".bt-gr");
  var btn = null;
  for(var b=0;b<btns.length;b++){
    if(btns[b].textContent.indexOf("Generar Siguiente Post")>=0){
      btn = btns[b];
      break;
    }
  }
  if(btn) btn.disabled = true;
  
  tryAllEndpoints(0);
}

function tryAllEndpoints(idx, retryCount){
  if(typeof retryCount==='undefined') retryCount = 0;
  // Use a copy to avoid race conditions if API_ENDPOINTS is modified
  var endpoints = API_ENDPOINTS.slice();
  
  if(idx >= endpoints.length){
    // All endpoints failed, use local data
    createPostFromLocal();
    var btns = document.querySelectorAll(".bt-gr");
    for(var b=0;b<btns.length;b++){
      if(btns[b].textContent.indexOf("Generar Siguiente Post")>=0){
        btns[b].disabled = false;
        break;
      }
    }
    return;
  }
  
  var url = endpoints[idx] + "/api/seo/niches?min_cpc=80";
  
  // ─── Cold start handling ───
  // Render se duerme tras 15 min. El primer request tarda ~30-60s.
  // Si falla con timeout, reintentamos con espera exponencial.
  var timeout = 5000; // 5s default
  if(endpoints[idx].indexOf("onrender.com")>=0 || endpoints[idx].indexOf("render")>=0){
    timeout = 30000; // 30s para Render (cold start)
  }
  
  fetch(url, {signal: AbortSignal.timeout(timeout)})
    .then(function(r){
      if(!r.ok) throw new Error("HTTP "+r.status);
      return r.json();
    })
    .then(function(data){
      var niches = data.niches || [];
      if(niches.length>0){
        createPostFromData(niches);
        var btns = document.querySelectorAll(".bt-gr");
        for(var b=0;b<btns.length;b++){
          if(btns[b].textContent.indexOf("Generar Siguiente Post")>=0){
            btns[b].disabled = false;
            break;
          }
        }
      } else {
        tryAllEndpoints(idx+1);
      }
    })
    .catch(function(err){
      // Cold start retry: si es Render y no hemos reintentado mucho
      if(endpoints[idx].indexOf("onrender.com")>=0 && retryCount < 3){
        var delay = (retryCount + 1) * 3000; // 3s, 6s, 9s
        showNotif("⏳ Cold start... reintento "+(retryCount+1)+"/3 en "+delay/1000+"s","var(--go)");
        setTimeout(function(){
          tryAllEndpoints(idx, retryCount + 1);
        }, delay);
      } else {
        tryAllEndpoints(idx+1);
      }
    });
}

function createPostFromData(niches){
  // Pick highest-CPC niche not yet used, or random
  var usedIds = generatedPosts.map(function(p){return p.id;});
  var available = niches.filter(function(n){return usedIds.indexOf(n.id)<0;});
  if(available.length===0) available = niches; // wrap around
  var niche = available[Math.floor(Math.random()*available.length)];
  
  // Generar el post
  finalizePost(niche);
  
  // Auto-publicar para Google
  autoPublishLatestPost();
}

function createPostFromLocal(){
  var usedIds = generatedPosts.map(function(p){return p.id;});
  var available = SHADOW_NICHES.filter(function(n){return usedIds.indexOf(n.id)<0;});
  if(available.length===0) available = SHADOW_NICHES;
  var niche = available[Math.floor(Math.random()*available.length)];
  finalizePost(niche);
}
function finalizePost(niche){
  var traffic = Math.floor(1000 + Math.random()*7000);
  var kwCount = (niche.kw||[]).length;
  var estimatedYield = (traffic * 0.02 * niche.cpc_avg).toFixed(2);
  var timestamp = new Date().toLocaleDateString("es-ES",{year:"numeric",month:"long",day:"numeric"});

  var kwList = (niche.kw||[]).slice(0,5);
  var primaryKW = kwList[0] || niche.name;
  var secondaryKW = kwList.length>1 ? kwList[1] : niche.name;

  var contentParagraphs = [
    "En el competitivo mundo de "+niche.name.toLowerCase()+", contar con información actualizada y relevante es fundamental para tomar decisiones acertadas. Este artículo explora los aspectos clave que debes considerar al buscar \'"+primaryKW+"\', una de las consultas con mayor intención comercial en el sector.",
    "El éxito en \'"+primaryKW+"\' depende en gran medida de entender las necesidades específicas de cada caso. Los expertos recomiendan evaluar múltiples opciones antes de comprometerse, comparando precios, servicios y experiencias de otros usuarios que hayan pasado por el mismo proceso.",
    "Estadísticas recientes muestran que las personas que invierten tiempo en investigar \'"+secondaryKW+"\' obtienen resultados significativamente mejores. Según datos del sector, el CPC promedio para este nicho es de $"+niche.cpc_avg.toFixed(0)+", lo que refleja su alto valor comercial y la competencia por captar clientes calificados.",
    "¿Cómo identificar al mejor proveedor de "+niche.name.toLowerCase()+"? Los factores clave incluyen la experiencia comprobada, las certificaciones relevantes, las opiniones de clientes anteriores y la transparencia en los precios. No te conformes con la primera opción; compara al menos tres alternativas antes de decidir.",
    "El proceso de selección puede parecer abrumador, pero con la guía adecuada se vuelve manejable. Recomendamos comenzar con una lista de preselección, verificar credenciales, solicitar presupuestos detallados y concertar una consulta inicial para evaluar la compatibilidad.",
    "La tendencia actual en \'"+primaryKW+"\' apunta hacia una mayor personalización y atención al detalle. Las empresas que lideran el mercado invierten en tecnología y capacitación continua para ofrecer un servicio superior, lo que se traduce en mejores resultados para sus clientes.",
    "No subestimes el poder de las referencias y testimonios. Hablar directamente con clientes anteriores puede darte una perspectiva única sobre lo que realmente ofrece cada servicio. Pregunta sobre resultados, tiempos de respuesta y nivel de satisfacción general antes de decidir.",
    "En resumen, encontrar el servicio ideal en \'"+primaryKW+"\' requiere paciencia, investigación y atención a los detalles. Sigue los consejos de esta guía y estarás mejor preparado para tomar una decisión informada que se ajuste a tus necesidades y presupuesto."
  ];

  var contentText = contentParagraphs.join('\n\n');
  var metaDesc = "Guía completa sobre "+niche.name.toLowerCase()+". Descubre todo lo que necesitas saber sobre \'"+primaryKW+"\'. Información actualizada con CPC de $"+niche.cpc_avg.toFixed(0)+". Consulta gratuita disponible.";

  var defaultFAQs = [
    {question: "¿Qué es "+niche.name.toLowerCase()+" y cómo funciona?", answer: niche.name+" es un servicio especializado en "+niche.cat.toLowerCase()+". Funciona evaluando las necesidades específicas de cada cliente y ofreciendo soluciones personalizadas con profesionales con años de experiencia en \'"+primaryKW+"\' y \'"+secondaryKW+"\'."},
    {question: "¿Cuánto cuesta contratar "+niche.name.toLowerCase()+"?", answer: "Los precios varían según la complejidad del caso. El CPC promedio en este nicho es de $"+niche.cpc_avg.toFixed(0)+", indicando un alto valor de mercado. Muchos servicios ofrecen consultas iniciales gratuitas."},
    {question: "¿Cómo elegir el mejor servicio de "+niche.name.toLowerCase()+"?", answer: "Compara al menos tres opciones, verifica credenciales, lee opiniones de clientes, solicita presupuestos detallados y asegúrate de que tengan experiencia en \'"+primaryKW+"\'. La transparencia es señal de un proveedor confiable."}
  ];

  var post = {
    id: niche.id,
    name: niche.name,
    cat: niche.cat,
    cpc: niche.cpc_avg,
    traffic: traffic,
    keywords: kwCount,
    keywordsStr: kwList.join(', '),
    yield: estimatedYield,
    timestamp: timestamp,
    status: "En Cola",
    metaDesc: metaDesc,
    content: contentText,
    faqs: defaultFAQs,
    kw: niche.kw
  };;
  localStorage.setItem("infinito_shadow_posts",JSON.stringify(generatedPosts));
  
  renderShadowPosts();
  updateShadowStats();
  showNotif("🌑 Nuevo post generado: "+niche.name+" | CPC: $"+niche.cpc_avg+" | Tráfico est.: "+traffic.toLocaleString()+"/mes","var(--cy)");
}

function renderShadowPosts(){
  var container = document.getElementById("shadow-posts-container");
  if(!container) return;
  if(generatedPosts.length===0){
    container.innerHTML = '<div style="padding:16px;text-align:center;color:var(--dim);font-size:10px">Aún no hay posts generados. Haz clic en "Generar Siguiente Post".</div>';
    return;
  }
  var html = '<div class="sec-tt" style="font-size:10px;margin-top:0">📄 Posts Generados <span style="font-size:8px;color:var(--dim);font-weight:400">— Haz clic para leer o editar</span></div>';
  for(var i=0;i<generatedPosts.length;i++){
    var p = generatedPosts[i];
    var statusClass = i===0 ? "bg bg-go" : "bg bg-gr";
    var statusText = i===0 ? "🆕 Recién" : "✅ Indexado";
    var editedMark = p.edited ? ' <span style="color:var(--go);font-size:8px">✏️ Editado</span>' : '';
    var publishedMark = p.published ? ' <span style="color:var(--grn);font-size:8px">📤 Pub.</span>' : '';
    html += '<div class="cd" style="margin-bottom:8px">';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">';
    html += '<div style="flex:1;min-width:150px;cursor:pointer" onclick="openPostViewer('+i+')">';
    html += '<div style="font-size:11px;color:var(--cy);font-weight:600">📝 '+(p.editedTitle||p.name)+''+editedMark+''+publishedMark+'</div>';
    html += '<div style="font-size:9px;color:var(--dim);margin-top:4px">CPC: $'+p.cpc+' · Tráfico: '+p.traffic.toLocaleString()+'/mes · Yield: $'+p.yield+' · '+p.timestamp+'</div>';
    html += '</div>';
    html += '<div style="display:flex;gap:4px;align-items:center">';
    html += '<div class="'+statusClass+'"><span class="dot"></span>'+statusText+'</div>';
    html += '<button class="bt" style="padding:3px 8px;font-size:8px;margin:0" onclick="openPostViewer('+i+')">👁️ Ver</button>';
    html += '<button class="bt bt-cy" style="padding:3px 8px;font-size:8px;margin:0" onclick="openPostEditor('+i+')">✏️</button>';
    html += '</div></div></div>';
  }
  container.innerHTML = html;
}

function updateShadowStats(){
  var totalPosts = generatedPosts.length;
  var totalKW = 0;
  var totalTraffic = 0;
  var totalYield = 0;
  for(var i=0;i<generatedPosts.length;i++){
    var p = generatedPosts[i];
    totalKW += p.keywords || 0;
    totalTraffic += p.traffic || 0;
    totalYield += parseFloat(p.yield) || 0;
  }
  var el = document.getElementById("shadow-posts");
  if(el) el.textContent = Math.max(5,totalPosts);
  var el2 = document.getElementById("shadow-keywords");
  if(el2) el2.textContent = Math.max(12,totalKW);
  var el3 = document.getElementById("shadow-traffic");
  // Preserve initial seed if no generated posts yet
  if(el3) el3.textContent = totalPosts>0 ? totalTraffic.toLocaleString() : "7,000";
  var el4 = document.getElementById("shadow-yield");
  if(el4) el4.textContent = totalPosts>0 ? "$"+totalYield.toFixed(2) : "$8,190.00";
}

// Load persisted posts on page load
renderShadowPosts();
updateShadowStats();

// ─── SHADOW SILO — AUTO-PILOT ───
var autoPilotConfig = JSON.parse(localStorage.getItem("infinito_autopilot")||'{}');
if(typeof autoPilotConfig.enabled==='undefined') autoPilotConfig.enabled = false;
if(typeof autoPilotConfig.interval==='undefined') autoPilotConfig.interval = 24;
if(typeof autoPilotConfig.strategy==='undefined') autoPilotConfig.strategy = 'rotating';
if(typeof autoPilotConfig.lastPostTime==='undefined') autoPilotConfig.lastPostTime = 0;
if(typeof autoPilotConfig.count==='undefined') autoPilotConfig.count = 0;

var autoPilotTimer = null;
var autoPilotIntervalMs = 60000; // check every minute

function autoPilotSaveConfig(){
  var stratEl = document.getElementById("autopilot-strategy");
  if(stratEl) autoPilotConfig.strategy = stratEl.value;
  localStorage.setItem("infinito_autopilot",JSON.stringify(autoPilotConfig));
  autoPilotRender();
}

function autoPilotToggle(){
  autoPilotConfig.enabled = !autoPilotConfig.enabled;
  if(autoPilotConfig.enabled){
    autoPilotConfig.lastPostTime = Date.now();
    autoPilotLog("🚀 Auto-Pilot activado. Intervalo: "+autoPilotConfig.interval+"h");
    if(!autoPilotTimer) autoPilotTimer = setInterval(autoPilotTick, autoPilotIntervalMs);
  } else {
    autoPilotLog("⏸️ Auto-Pilot desactivado");
    if(autoPilotTimer){
      clearInterval(autoPilotTimer);
      autoPilotTimer = null;
    }
  }
  autoPilotSaveConfig();
}

function autoPilotUpdateInterval(val){
  autoPilotConfig.interval = parseInt(val);
  var label = document.getElementById("autopilot-interval-label");
  if(label) label.textContent = val+"h";
  autoPilotSaveConfig();
}

function autoPilotGenerateNow(){
  var strategy = autoPilotConfig.strategy;
  var usedIds = generatedPosts.map(function(p){return p.id;});
  var available = SHADOW_NICHES.slice();
  
  if(strategy === 'rotating'){
    var unused = available.filter(function(n){return usedIds.indexOf(n.id)<0;});
    if(unused.length>0) available = unused;
  }
  
  var niche;
  if(strategy === 'highest-cpc'){
    available.sort(function(a,b){return b.cpc_avg - a.cpc_avg});
    niche = available[0];
  } else {
    niche = available[Math.floor(Math.random()*available.length)];
  }
  
  if(!niche) niche = SHADOW_NICHES[Math.floor(Math.random()*SHADOW_NICHES.length)];
  finalizePost(niche);
  
  autoPilotConfig.lastPostTime = Date.now();
  autoPilotConfig.count++;
  autoPilotLog("🤖 Post generado automáticamente: "+niche.name);
  autoPilotSaveConfig();
}

function autoPilotTick(){
  if(!autoPilotConfig.enabled) return;
  var elapsedHours = (Date.now() - autoPilotConfig.lastPostTime) / 3600000;
  if(elapsedHours >= autoPilotConfig.interval){
    autoPilotGenerateNow();
  }
  autoPilotRender();
}

function autoPilotRender(){
  // Status
  var statusEl = document.getElementById("autopilot-status");
  var toggleBtn = document.getElementById("autopilot-toggle-btn");
  
  if(statusEl){
    statusEl.innerHTML = autoPilotConfig.enabled
      ? '<span style="color:var(--grn)">▶️ Activo</span>'
      : '<span style="color:var(--dim)">⏸️ Apagado</span>';
  }
  if(toggleBtn){
    toggleBtn.textContent = autoPilotConfig.enabled ? "⏸️ Pausar" : "▶️ Activar";
    toggleBtn.className = autoPilotConfig.enabled ? "bt bt-go" : "bt bt-gr";
  }
  
  // Count
  var countEl = document.getElementById("autopilot-count");
  if(countEl) countEl.textContent = autoPilotConfig.count;
  
  // Next post time
  var nextEl = document.getElementById("autopilot-next");
  if(nextEl){
    if(!autoPilotConfig.enabled) {
      nextEl.textContent = "—";
    } else {
      var remaining = (autoPilotConfig.interval * 3600000) - (Date.now() - autoPilotConfig.lastPostTime);
      if(remaining <= 0) {
        nextEl.textContent = "⚠️ Pendiente...";
      } else {
        var hrs = Math.floor(remaining / 3600000);
        var mins = Math.floor((remaining % 3600000) / 60000);
        nextEl.textContent = hrs+"h "+mins+"m";
      }
    }
  }
  
  // Progress bar
  var bar = document.getElementById("autopilot-progress-bar");
  var pctEl = document.getElementById("autopilot-progress-pct");
  if(bar && pctEl){
    var elapsed = Date.now() - autoPilotConfig.lastPostTime;
    var total = autoPilotConfig.interval * 3600000;
    var pct = Math.min(100, (elapsed / total) * 100);
    if(!autoPilotConfig.enabled) pct = 0;
    bar.style.width = pct+"%";
    pctEl.textContent = autoPilotConfig.enabled ? Math.floor(pct)+"%" : "0%";
  }
  
  // Strategy select
  var stratEl = document.getElementById("autopilot-strategy");
  if(stratEl) stratEl.value = autoPilotConfig.strategy;
  
  // Interval slider
  var sliderEl = document.getElementById("autopilot-interval");
  if(sliderEl) sliderEl.value = autoPilotConfig.interval;
  var labelEl = document.getElementById("autopilot-interval-label");
  if(labelEl) labelEl.textContent = autoPilotConfig.interval+"h";
}

function autoPilotLog(msg){
  var logEl = document.getElementById("autopilot-log");
  if(!logEl) return;
  var time = new Date().toLocaleTimeString("es-ES",{hour:"2-digit",minute:"2-digit"});
  logEl.innerHTML = '<div>['+time+'] '+msg+'</div>' + logEl.innerHTML;
  // Keep max 20 lines
  while(logEl.children.length > 20) logEl.removeChild(logEl.lastChild);
}

// Start Auto-Pilot
if(autoPilotConfig.enabled){
  autoPilotLog("🚀 Auto-Pilot reanudado (intervalo: "+autoPilotConfig.interval+"h)");
  autoPilotTimer = setInterval(autoPilotTick, autoPilotIntervalMs);
} else {
  autoPilotLog("⏸️ Auto-Pilot apagado. Actívalo para generación automática.");
}
autoPilotRender();
autoPilotTick();

// ─── SHADOW SILO — EDITOR DE POSTS ───
function openPostEditor(index){
  var overlay = document.getElementById("editor-overlay");
  if(!overlay) return;
  var post = generatedPosts[index];
  if(!post) return;
  
  document.getElementById("editor-index").value = index;
  document.getElementById("editor-title").value = post.editedTitle || post.name || '';
  document.getElementById("editor-niche").value = post.cat || post.name || '';
  document.getElementById("editor-cpc").value = post.cpc || '';
  document.getElementById("editor-traffic").value = post.traffic || '';
  document.getElementById("editor-yield").value = '$'+(post.yield||'0.00');
  
  // Keywords
  var kwStr = '';
  if(post.keywordsStr) kwStr = post.keywordsStr;
  else if(post.kw && post.kw.length) kwStr = post.kw.join(', ');
  document.getElementById("editor-keywords").value = kwStr;
  
  // Meta description
  document.getElementById("editor-metadesc").value = post.metaDesc || 'Guía completa sobre '+post.name+'. CPC: $'+post.cpc+'. Información actualizada.';
  
  // Content
  document.getElementById("editor-content").value = post.content || 'Contenido del artículo sobre '+post.name+'. Este es un post generado automáticamente por el Shadow Silo del Proyecto Infinito.';
  
  // FAQs
  renderFAQFields(post.faqs || []);
  
  document.getElementById("editor-preview").textContent = 'Haz clic en "Previsualizar HTML" para ver el código generado.';
  overlay.classList.add("act");
  document.body.style.overflow = "hidden";
}

function closePostEditor(){
  var overlay = document.getElementById("editor-overlay");
  if(!overlay) return;
  overlay.classList.remove("act");
  document.body.style.overflow = "";
}

function savePostEdit(){
  var idx = parseInt(document.getElementById("editor-index").value);
  if(idx<0 || idx>=generatedPosts.length) return;
  var post = generatedPosts[idx];
  
  post.editedTitle = document.getElementById("editor-title").value.trim() || post.name;
  post.cpc = parseFloat(document.getElementById("editor-cpc").value) || post.cpc;
  post.traffic = parseInt(document.getElementById("editor-traffic").value) || post.traffic;
  post.keywordsStr = document.getElementById("editor-keywords").value.trim();
  post.metaDesc = document.getElementById("editor-metadesc").value.trim();
  post.content = document.getElementById("editor-content").value.trim();
  post.cat = document.getElementById("editor-niche").value.trim() || post.cat;
  post.edited = true;
  
  // Recalculate yield
  var ctr = 0.02;
  post.yield = (post.traffic * ctr * post.cpc).toFixed(2);
  
  // Save FAQs
  post.faqs = [];
  var faqEls = document.querySelectorAll(".faq-item-ed");
  for(var f=0;f<faqEls.length;f++){
    var q = faqEls[f].querySelector(".faq-q-inp");
    var a = faqEls[f].querySelector(".faq-a-inp");
    if(q && a && q.value.trim() && a.value.trim()){
      post.faqs.push({question: q.value.trim(), answer: a.value.trim()});
    }
  }
  
  generatedPosts[idx] = post;
  localStorage.setItem("infinito_shadow_posts",JSON.stringify(generatedPosts));
  renderShadowPosts();
  updateShadowStats();
  showNotif("💾 Post guardado: "+post.editedTitle,"var(--grn)");
}

function renderFAQFields(faqs){
  var container = document.getElementById("editor-faqs");
  if(!container) return;
  if(!faqs || faqs.length===0){
    faqs = [{question:"¿Qué es "+document.getElementById("editor-title").value+"?",answer:"Es un servicio/proyecto relacionado con..."}];
  }
  var html = '';
  for(var i=0;i<faqs.length;i++){
    html += '<div class="faq-item-ed">';
    html += '<button class="faq-del" onclick="removeFAQField(this)">✕</button>';
    html += '<input class="inp faq-q-inp" type="text" placeholder="Pregunta..." value="'+escapeHTML(faqs[i].question)+'" style="font-size:10px;margin-bottom:4px">';
    html += '<textarea class="inp inp-ta faq-a-inp" placeholder="Respuesta..." style="font-size:10px;min-height:40px">'+escapeHTML(faqs[i].answer)+'</textarea>';
    html += '</div>';
  }
  container.innerHTML = html;
}

function addFAQField(){
  var container = document.getElementById("editor-faqs");
  if(!container) return;
  var div = document.createElement("div");
  div.className = "faq-item-ed";
  div.innerHTML = '<button class="faq-del" onclick="removeFAQField(this)">✕</button><input class="inp faq-q-inp" type="text" placeholder="Pregunta..." style="font-size:10px;margin-bottom:4px"><textarea class="inp inp-ta faq-a-inp" placeholder="Respuesta..." style="font-size:10px;min-height:40px"></textarea>';
  container.appendChild(div);
  showNotif("➕ Nueva FAQ agregada","var(--cy)");
}

function removeFAQField(btn){
  var item = btn.parentElement;
  if(item) item.parentElement.removeChild(item);
}

function escapeHTML(str){
  if(typeof str!=='string') return '';
  return str.replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function generatePostHTML(post){
  var title = post.editedTitle || post.name;
  var niche = post.cat || 'SEO';
  var cpc = post.cpc || 0;
  var traffic = post.traffic || 0;
  var yieldVal = post.yield || '0.00';
  var keywords = post.keywordsStr || (post.kw?post.kw.join(', '):title);
  var metaDesc = post.metaDesc || 'Guía completa sobre '+title+'. Información actualizada con CPC de $'+cpc+'. Consulta gratuita disponible.';
  var content = post.content || 'Contenido del artículo sobre '+title+'.';
  var faqs = post.faqs || [];
  var slug = title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'') || 'post';
  var date = new Date().toISOString().split('T')[0];
  
  // Build FAQ Schema JSON-LD
  var faqSchema = '';
  if(faqs.length>0){
    var items = faqs.map(function(f){
      return '        {"@type":"Question","name":'+JSON.stringify(f.question)+',"acceptedAnswer":{"@type":"Answer","text":'+JSON.stringify(f.answer)+'}}';
    });
    faqSchema = '{\n    "@context": "https://schema.org",\n    "@type": "FAQPage",\n    "mainEntity": [\n'+items.join(',\n')+'\n    ]\n}';
  }
  
  // Article Schema
  var articleSchema = '{\n    "@context": "https://schema.org",\n    "@type": "Article",\n    "headline": '+JSON.stringify(title)+',\n    "description": '+JSON.stringify(metaDesc)+',\n    "datePublished": "'+date+'",\n    "dateModified": "'+date+'",\n    "author": {"@type":"Person","name":"Proyecto Infinito"},\n    "publisher": {"@type":"Organization","name":"Proyecto Infinito"}\n}';
  
  // Build HTML
 
  // Insert Monetag ad script in head if configured
  var monetagScript = '';
  if(monetagEnabled && monetagSiteID){
    monetagScript = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-'+monetagSiteID+'" crossorigin="anonymous"><\/script>\n';
    monetagScript += '<script>\n(adsbygoogle = window.adsbygoogle || []).push({});\n<\/script>\n';
  }
  var html = '<!DOCTYPE html>\n<html lang="es">\n<head>\n';
  html += '    <meta charset="UTF-8">\n';
  html += '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n';
  html += '    <title>'+escapeHTML(title)+'</title>\n';
  html += '    <meta name="description" content="'+escapeHTML(metaDesc)+'">\n';
  html += '    <meta name="keywords" content="'+escapeHTML(keywords)+'">\n';
  html += '    <meta name="robots" content="index, follow">\n';
  html += '    <meta property="og:type" content="article">\n';
  html += '    <meta property="og:title" content="'+escapeHTML(title)+'">\n';
  html += '    <meta property="og:description" content="'+escapeHTML(metaDesc)+'">\n';
  html += '    <meta property="og:locale" content="es_ES">\n';
  html += '    <meta name="twitter:card" content="summary_large_image">\n';
  html += '    <meta name="twitter:title" content="'+escapeHTML(title)+'">\n';
  html += '    <link rel="canonical" href="https://proyectoinfinito.com/'+slug+'/">\n';
  if(monetagScript) html += '    '+monetagScript;
  if(faqSchema) html += '    <script type="application/ld+json">\n'+faqSchema+'\n    <\/script>\n';
  html += '    <script type="application/ld+json">\n'+articleSchema+'\n    <\/script>\n';
  html += '    <style>\n';
  html += '        *{margin:0;padding:0;box-sizing:border-box}\n';
  html += '        :root{--bg:#050508;--grn:#00ff41;--cy:#00f0ff;--text:#c8d6e5;--dim:#2d2d44;--card:#0a0a14;--border:rgba(0,255,65,0.12)}\n';
  html += '        body{font-family:\'Courier New\',monospace;background:var(--bg);color:var(--text);line-height:1.8}\n';
  html += '        .container{max-width:900px;margin:0 auto;padding:20px}\n';
  html += '        h1{font-size:26px;color:var(--cy);margin:20px 0 12px}\n';
  html += '        h2{font-size:18px;color:var(--grn);margin:28px 0 12px;border-bottom:1px solid var(--border)}\n';
  html += '        h3{font-size:14px;color:var(--cy);margin:18px 0 8px}\n';
  html += '        p{font-size:13px;margin:10px 0}\n';
  html += '        ul,ol{margin:10px 0 10px 20px}\n';
  html += '        li{font-size:13px;margin:6px 0}\n';
  html += '        .badge{font-size:10px;color:var(--grn);text-transform:uppercase;letter-spacing:2px;display:flex;align-items:center;gap:6px;margin-bottom:8px}\n';
  html += '        .badge .dot{width:5px;height:5px;border-radius:50%;background:var(--grn);animation:pulse 2s ease-in-out infinite}\n';
  html += '        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}\n';
  html += '        .intro{padding:16px;border-left:2px solid var(--grn);background:rgba(0,255,65,0.02);margin-bottom:24px;font-size:13px}\n';
  html += '        .cta{margin:30px 0;padding:20px;border:1px solid var(--border);text-align:center;background:rgba(0,255,65,0.03)}\n';
  html += '        .cta .btn{display:inline-block;padding:10px 28px;border:1px solid var(--grn);color:var(--grn);text-decoration:none;font-size:11px;letter-spacing:2px;text-transform:uppercase;transition:all 0.3s}\n';
  html += '        .cta .btn:hover{background:var(--grn);color:#000}\n';
  html += '        .faq-item{padding:14px 16px;border:1px solid var(--border);margin-bottom:8px}\n';
  html += '        .faq-q{font-size:12px;color:var(--cy);font-weight:600;margin-bottom:6px}\n';
  html += '        .faq-a{font-size:12px;color:var(--dim);line-height:1.7}\n';
  html += '        footer{margin-top:40px;padding:16px 0;border-top:1px solid var(--border);text-align:center;font-size:9px;color:var(--dim)}\n';
  html += '    <\/style>\n';
  html += '</head>\n<body>\n<div class="container">\n';
  html += '    <header><div class="badge"><span class="dot"></span> PROYECTO INFINITO &middot; '+escapeHTML(niche)+'</div><h1>'+escapeHTML(title)+'</h1></header>\n';
  html += '    <div class="intro">'+escapeHTML(metaDesc)+'</div>\n';
  html += '    <div class="content">'+content.replace(/\n/g,'\n    <p>').replace(/<p><p>/g,'<p>')+'</div>\n';
  
  if(faqs.length>0){
    html += '    <div class="cta"><p>¿Tienes preguntas? Cont&aacute;ctanos para una consulta gratuita.</p><a href="#" class="btn">Solicitar Consulta</a></div>\n';
    html += '    <h2>Preguntas Frecuentes</h2>\n';
    for(var f=0;f<faqs.length;f++){
      html += '    <div class="faq-item"><div class="faq-q">'+escapeHTML(faqs[f].question)+'</div><div class="faq-a">'+escapeHTML(faqs[f].answer)+'</div></div>\n';
    }
  }
  
  html += '    <footer><strong>PROYECTO INFINITO</strong> &mdash; Generado por Shadow Silo &middot; CPC: $'+cpc+' &middot; '+date+'</footer>\n';
  html += '</div>\n</body>\n</html>';
  
  return {html: html, slug: slug, title: title};
}

function previewPostHTML(){
  var idx = parseInt(document.getElementById("editor-index").value);
  if(idx<0 || idx>=generatedPosts.length) return;
  var post = generatedPosts[idx];
  
  // Temporarily save to get latest values
  post.editedTitle = document.getElementById("editor-title").value.trim() || post.name;
  post.cpc = parseFloat(document.getElementById("editor-cpc").value) || post.cpc;
  post.traffic = parseInt(document.getElementById("editor-traffic").value) || post.traffic;
  post.keywordsStr = document.getElementById("editor-keywords").value.trim();
  post.metaDesc = document.getElementById("editor-metadesc").value.trim();
  post.content = document.getElementById("editor-content").value.trim();
  post.cat = document.getElementById("editor-niche").value.trim() || post.cat;
  
  // Get FAQs from DOM
  post.faqs = [];
  var faqEls = document.querySelectorAll(".faq-item-ed");
  for(var f=0;f<faqEls.length;f++){
    var q = faqEls[f].querySelector(".faq-q-inp");
    var a = faqEls[f].querySelector(".faq-a-inp");
    if(q && a && q.value.trim() && a.value.trim()){
      post.faqs.push({question: q.value.trim(), answer: a.value.trim()});
    }
  }
  
    // El HTML se genera en el servidor via build_post_html()
  var preview = document.getElementById("editor-preview");
  if(preview){
    var html = result.html;
    // Truncate for preview
    if(html.length>2000) html = html.slice(0,2000)+'\n\n... (truncado, '+result.html.length+' bytes totales)';
    preview.textContent = html;
    preview.scrollTop = 0;
  }
  showNotif("👁️ HTML generado: "+(result.html.length/1024).toFixed(1)+" KB","var(--cy)");
}

function publishPostHTML(){
  var idx = parseInt(document.getElementById("editor-index").value);
  if(idx<0 || idx>=generatedPosts.length) return;
  
  // Save first
  savePostEdit();
  
  var post = generatedPosts[idx];
  var result = generatePostHTML(post);
  
  // Create download link
  var blob = new Blob([result.html], {type: 'text/html;charset=utf-8'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = result.slug + '.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  // Mark as published
  post.published = true;
  post.publishedAt = new Date().toISOString();
  localStorage.setItem("infinito_shadow_posts",JSON.stringify(generatedPosts));
  renderShadowPosts();
  
  showNotif("📤 HTML publicado: "+result.slug+".html ("+(result.html.length/1024).toFixed(1)+" KB)", "var(--cy)");
// ─── OPENROUTER IA — CONFIG & GENERATE ───
var orAPIKey = localStorage.getItem("infinito_or_key") || "";
var orModel = localStorage.getItem("infinito_or_model") || "google/gemini-2.0-flash-lite-preview";

function toggleORConfig(){
  var form = document.getElementById("or-config-form");
  if(!form) return;
  form.style.display = form.style.display==="none"?"block":"none";
  if(form.style.display==="block"){
    var inp = document.getElementById("or-api-key");
    if(inp) inp.value = orAPIKey;
    var sel = document.getElementById("or-model");
    if(sel) sel.value = orModel;
  }
}

function toggleORKeyVisibility(){
  var inp = document.getElementById("or-api-key");
  if(inp) inp.type = inp.type==="password"?"text":"password";
}

function saveORConfig(){
  var inp = document.getElementById("or-api-key");
  var sel = document.getElementById("or-model");
  if(inp) orAPIKey = inp.value.trim();
  if(sel) orModel = sel.value;
  localStorage.setItem("infinito_or_key", orAPIKey);
  localStorage.setItem("infinito_or_model", orModel);
  updateORDisplay();
  showNotif("🤖 Configuración de OpenRouter guardada","var(--cy)");
}

function updateORDisplay(){
  var el = document.getElementById("or-status");
  if(!el) return;
  if(orAPIKey && orAPIKey.startsWith("sk-or-")){
    var masked = orAPIKey.slice(0,8)+"...";
    el.textContent = "✅ Conectado ("+masked+") · "+orModel.split("/")[1];
    el.style.color = "var(--grn)";
  } else {
    el.textContent = "⚠️ No configurado";
    el.style.color = "var(--go)";
  }
}

async function generateWithIA(){
  var btn = document.getElementById("btn-generate-ia");
  if(!btn) return;
  
  // Verificar config
  if(!orAPIKey || !orAPIKey.startsWith("sk-or-")){
    showNotif("❌ Configura tu API Key de OpenRouter primero (🤖 en la sección de abajo)","var(--rd)");
    toggleORConfig();
    return;
  }
  
  // Elegir nicho
  var usedIds = generatedPosts.map(function(p){return p.id;});
  var available = SHADOW_NICHES.filter(function(n){return usedIds.indexOf(n.id)<0;});
  if(available.length===0) available = SHADOW_NICHES;
  var niche = available[Math.floor(Math.random()*available.length)];
  
  btn.disabled = true;
  btn.textContent = "⏳ Generando...";
  showNotif("🤖 Llamando a OpenRouter IA para: "+niche.name+"...","var(--cy)");
  
  // Llamar al API endpoint con la key
  var endpoints = API_ENDPOINTS.slice();
  var success = false;
  
  for(var e=0;e<endpoints.length;e++){
    try {
      var resp = await fetch(endpoints[e]+"/api/seo/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer "+orAPIKey,
          "X-OpenRouter-Key": orAPIKey
        },
        body: JSON.stringify({
          niche_name: niche.name,
          niche_cat: niche.cat,
          cpc: niche.cpc_avg,
          keywords: niche.kw || [],
          language: "es"
        ,
          api_key: orAPIKey
        }),
        signal: AbortSignal.timeout(60000)
      });
      
      if(resp.ok){
        var data = await resp.json();
        if(data.success){
          // Crear post con contenido generado por IA
          var traffic = Math.floor(2000 + Math.random()*8000);
          var estimatedYield = (traffic * 0.02 * niche.cpc_avg).toFixed(2);
          var timestamp = new Date().toLocaleDateString("es-ES",{year:"numeric",month:"long",day:"numeric"});
          
          var post = {
            id: niche.id+"-ia-"+Date.now(),
            name: niche.name,
            cat: niche.cat,
            cpc: niche.cpc_avg,
            traffic: traffic,
            keywords: (niche.kw||[]).length,
            keywordsStr: (niche.kw||[]).join(", "),
            yield: estimatedYield,
            timestamp: timestamp,
            status: "Nuevo (IA)",
            metaDesc: data.meta_description || "",
            content: data.content || "",
            faqs: data.faqs || [],
            editedTitle: data.title || niche.name,
            edited: true,
            ia_generated: true
          };
          
          generatedPosts.unshift(post);
          localStorage.setItem("infinito_shadow_posts",JSON.stringify(generatedPosts));
          renderShadowPosts();
          updateShadowStats();
          
          showNotif("✅ Artículo generado con IA: "+data.title+" | $"+(traffic*0.02*niche.cpc_avg).toFixed(2)+"/mes","var(--grn)");
          success = true;
          break;
        }
      }
    } catch(err) {
      console.warn("Endpoint "+endpoints[e]+" failed:", err);
    }
  }
  
  if(!success){
    // Fallback: generar con datos locales
    showNotif("⚠️ API no disponible, usando generación local","var(--go)");
    finalizePost(niche);
  }
  
  btn.disabled = false;
  btn.textContent = "🤖 Generar con IA";
}

// Restore OR display on load
(function(){
  updateORDisplay();
})();

// ─── SHADOW SILO — POST VIEWER & PUBLISH ───
var viewerCurrentIndex = -1;
var monetagSiteID = localStorage.getItem("infinito_monetag_siteid") || "";
var monetagEnabled = localStorage.getItem("infinito_monetag_enabled") === "true";

function toggleMonetagConfig(){
  var form = document.getElementById("monetag-config-form");
  if(!form) return;
  form.style.display = form.style.display==="none"?"block":"none";
  if(form.style.display==="block"){
    var inp = document.getElementById("monetag-site-id");
    if(inp) inp.value = monetagSiteID;
    var chk = document.getElementById("monetag-enabled");
    if(chk) chk.checked = monetagEnabled;
  }
}

function saveMonetagConfig(){
  var inp = document.getElementById("monetag-site-id");
  var chk = document.getElementById("monetag-enabled");
  if(inp) monetagSiteID = inp.value.trim();
  // Validate: Site ID must be numeric
  if(monetagSiteID && !/^\d+$/.test(monetagSiteID)){
    showNotif("❌ Site ID inválido: debe ser solo números","var(--rd)");
    return;
  }
  if(chk) monetagEnabled = chk.checked && monetagSiteID.length > 0;
  localStorage.setItem("infinito_monetag_siteid", monetagSiteID);
  localStorage.setItem("infinito_monetag_enabled", monetagEnabled ? "true" : "false");
  updateMonetagDisplay();
  showNotif("📢 Configuración de Monetag guardada","var(--go)");
}

function updateMonetagDisplay(){
  var el = document.getElementById("monetag-status");
  if(el){
    el.textContent = monetagEnabled && monetagSiteID ? "✅ Activo (ID: "+monetagSiteID+")" : "⏸️ Desactivado";
    el.style.color = monetagEnabled && monetagSiteID ? "var(--grn)" : "var(--go)";
  }
}

function openPostViewer(index){
  var overlay = document.getElementById("viewer-overlay");
  if(!overlay) return;
  var post = generatedPosts[index];
  if(!post) return;
  viewerCurrentIndex = index;
  renderPostContent(post);
  overlay.classList.add("act");
  document.body.style.overflow = "hidden";
}

function closePostViewer(){
  var overlay = document.getElementById("viewer-overlay");
  if(!overlay) return;
  overlay.classList.remove("act");
  document.body.style.overflow = "";
  viewerCurrentIndex = -1;
}

function renderPostContent(post){
  var container = document.getElementById("viewer-content");
  var titleBar = document.getElementById("viewer-bar-title");
  if(!container) return;

  var title = post.editedTitle || post.name;
  var niche = post.cat || "SEO";
  var cpc = post.cpc || 0;
  var traffic = post.traffic || 0;
  var content = post.content || "";
  var metaDesc = post.metaDesc || "";
  var faqs = post.faqs || [];
  var timestamp = post.timestamp || new Date().toLocaleDateString("es-ES",{year:"numeric",month:"long",day:"numeric"});

  if(titleBar) titleBar.textContent = "📄 "+title;

  // Build silo links from other posts in same category
  var siloLinks = '';
  var related = [];
  for(var i=0;i<generatedPosts.length;i++){
    var p = generatedPosts[i];
    if(p.id !== post.id && p.cat === post.cat){
      related.push(p);
    }
  }
  if(related.length>0){
    siloLinks = '<div class="viewer-silo-nav"><div class="viewer-silo-nav-tt">📎 Contenido Relacionado</div><div class="viewer-silo-links">';
    for(var r=0;r<Math.min(related.length,5);r++){
      var ridx = generatedPosts.indexOf(related[r]);
      siloLinks += '<a href="#" onclick="openPostViewer('+ridx+');return false">📝 '+escapeHTML(related[r].editedTitle||related[r].name)+'</a>';
    }
    siloLinks += '</div></div>';
  }

  // Build Monetag ad block for inline injection
  var monetagAd = '';
  if(monetagEnabled && monetagSiteID){
    monetagAd = '<div class="viewer-ad"><div class="viewer-ad-lb">— Publicidad —</div>';
    monetagAd += '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-'+monetagSiteID+'" crossorigin="anonymous"><\/script>';
    monetagAd += '</div>';
  }

  var bodyHtml = '';
  if(content){
    var paragraphs = content.split('
').filter(function(l){return l.trim().length>0;});
    for(var p=0;p<paragraphs.length;p++){
      bodyHtml += '<p>'+escapeHTML(paragraphs[p])+'</p>';
      if(p===2 && monetagAd) bodyHtml += monetagAd;
    }
  } else {
    bodyHtml = '<p>Contenido del artículo sobre '+escapeHTML(title)+'.</p>';
  }

  // FAQ section
  var faqHtml = '';
  if(faqs.length>0){
    faqHtml = '<h2>Preguntas Frecuentes</h2>';
    for(var f=0;f<faqs.length;f++){
      faqHtml += '<div class="viewer-faq"><div class="viewer-faq-q">'+escapeHTML(faqs[f].question)+'</div><div class="viewer-faq-a">'+escapeHTML(faqs[f].answer)+'</div></div>';
    }
  }

  // CTA section
  var ctaHtml = '<div class="viewer-cta"><p>¿Necesitas ayuda con '+escapeHTML(title)+'? Contáctanos para una consulta gratuita.</p><a href="#" class="btn">Solicitar Consulta →</a></div>';

  // Footer ad
  var footerAd = '';
  if(monetagEnabled && monetagSiteID){
    footerAd = '<div class="viewer-ad" style="margin-top:12px"><div class="viewer-ad-lb">— Anuncio —</div>';
    footerAd += '<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-'+monetagSiteID+'" data-ad-slot="9876543210" data-ad-format="auto"><\/ins>';
    footerAd += '<script>(adsbygoogle = window.adsbygoogle || []).push({});<\/script></div>';
  }

  // Disclaimer
  var disclaimer = '<div class="viewer-disclaimer"><strong>⚠️ Aviso:</strong> Este contenido es informativo y no constituye asesoría profesional. Consulta con un especialista certificado.</div>';

  var html = '';
  html += '<h1>'+escapeHTML(title)+'</h1>';
  html += '<div class="viewer-meta"><span>📂 '+escapeHTML(niche)+'</span><span>💰 CPC: $'+cpc+'</span><span>📊 Tráfico est.: '+traffic.toLocaleString()+'/mes</span><span>📅 '+timestamp+'</span></div>';
  if(metaDesc) html += '<div class="viewer-intro">'+escapeHTML(metaDesc)+'</div>';
  html += siloLinks;
  html += bodyHtml;
  html += ctaHtml;
  html += faqHtml;
  html += footerAd;
  html += disclaimer;
  html += '<div class="viewer-footer"><strong>PROYECTO INFINITO</strong> &mdash; Generado por Shadow Silo &middot; Publicación relacionada con '+escapeHTML(niche)+'</div>';

  container.innerHTML = html;
  container.scrollTop = 0;
}

function publishToDApp(){
  var idx = viewerCurrentIndex;
  if(idx<0 || idx>=generatedPosts.length) {
    showNotif("❌ No hay post seleccionado para publicar","var(--rd)");
    return;
  }
  var post = generatedPosts[idx];
  var result = generatePostHTML(post);

  // Mark as published
  post.published = true;
  post.publishedAt = new Date().toISOString();
  post.publishedSlug = result.slug;
  generatedPosts[idx] = post;
  localStorage.setItem("infinito_shadow_posts",JSON.stringify(generatedPosts));
  renderShadowPosts();

  // Save to published posts list
  var published = JSON.parse(localStorage.getItem("infinito_published_posts")||"[]");
  published.unshift({
    slug: result.slug,
    title: result.title,
    html: result.html,
    date: new Date().toISOString().split('T')[0]
  });
  localStorage.setItem("infinito_published_posts",JSON.stringify(published));

  // Generate and download sitemap
  generateSitemap();

  showNotif("📤 Publicado en DApp: "+result.title+" ("+(result.html.length/1024).toFixed(1)+" KB)","var(--grn)");
  closePostViewer();
}

  // Auto-publicar en el API de Vercel para que Google pueda indexarlo
  var monetagID = localStorage.getItem('infinito_monetag_siteid') || '';
  var endpoints = API_ENDPOINTS.slice();
  for(var e=0;e<endpoints.length;e++){
    try {
      fetch(endpoints[e]+'/api/publish-post', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          slug: result.slug,
          title: post.editedTitle || post.name,
          content: post.content || '',
          meta_description: post.metaDesc || '',
          niche_name: post.name,
          niche_cat: post.cat || 'SEO',
          cpc: post.cpc || 0,
          keywords: post.keywordsStr || '',
          monetag_site_id: monetagID
        })
      }).then(function(r){
        if(r.ok) console.log('Post auto-publicado en '+endpoints[e]);
      }).catch(function(e){});
      break; // Solo intentar el primer endpoint que funcione
    } catch(e){}
  }

function generateSitemap(){
  var published = JSON.parse(localStorage.getItem("infinito_published_posts")||"[]");
  if(published.length===0) return;
  var sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n';
  sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  for(var i=0;i<published.length;i++){
    var p = published[i];
    sitemap += '  <url>\n';
    sitemap += '    <loc>https://proyectoinfinito.com/posts/'+p.slug+'/</loc>\n';
    sitemap += '    <lastmod>'+p.date+'</lastmod>\n';
    sitemap += '    <priority>0.8</priority>\n';
    sitemap += '  </url>\n';
  }
  sitemap += '</urlset>';
  localStorage.setItem("infinito_sitemap", sitemap);

  // Trigger download
  var blob = new Blob([sitemap], {type:'application/xml'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "sitemap.xml";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(function(){URL.revokeObjectURL(url);}, 1000);
}


// ─── AUTO-PUBLISH (para que Google indexe los posts) ───
function autoPublishLatestPost(){
  if(generatedPosts.length === 0) return;
  var post = generatedPosts[0];
  if(!post) return;
  
  var title = post.editedTitle || post.name;
  var slug = title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'') || 'post';
  var monetagID = (typeof monetagSiteID !== 'undefined') ? monetagSiteID : '';
  
  // Generar HTML completo y publicar en API
  var result = generatePostHTML(post);
  
  var endpoints = API_ENDPOINTS.slice();
  for(var e=0;e<endpoints.length;e++){
    try {
      fetch(endpoints[e]+'/api/publish-post', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          slug: slug,
          title: title,
          content: post.content || '',
          meta_description: post.metaDesc || '',
          niche_name: post.name,
          niche_cat: post.cat || 'SEO',
          cpc: post.cpc || 0,
          keywords: post.keywordsStr || '',
          monetag_site_id: monetagID
        })
      }).then(function(r){
        if(r.ok){
          console.log('✅ Post auto-publicado: '+slug);
          // Marcar como publicado
          post.published = true;
          post.publishedSlug = slug;
          localStorage.setItem('infinito_shadow_posts',JSON.stringify(generatedPosts));
          renderShadowPosts();
        }
      }).catch(function(err){
        console.warn('Auto-publish failed:', err);
      });
      break;
    } catch(e){}
  }
}
// Restore Monetag display on load
(function(){
  updateMonetagDisplay();
})();

KB)","var(--grn)");
}

// ─── HEALTH TRACKER — INYECCIONES Y SÍNTOMAS ───
var healthData = JSON.parse(localStorage.getItem("infinito_health")||'{"injections":[],"symptoms":[]}');

function saveHealthData(){
  localStorage.setItem("infinito_health",JSON.stringify(healthData));
  renderHealthTracker();
}

function markInjection(){
  var now = new Date();
  healthData.injections.push({date:now.toISOString(),type:"inyección diaria"});
  saveHealthData();
  showNotif("💉 Inyección registrada: "+now.toLocaleString("es-ES"),"var(--grn)");
}

function clearInjections(){
  if(!confirm("¿Borrar todo el historial de inyecciones?")) return;
  healthData.injections = [];
  saveHealthData();
  showNotif("🗑️ Historial de inyecciones borrado","var(--rd)");
}

function addSymptom(){
  var text = document.getElementById("symptom-text");
  var sev = document.getElementById("symptom-severity");
  if(!text || !text.value.trim()){
    showNotif("❌ Describe el síntoma primero","var(--rd)");
    return;
  }
  healthData.symptoms.push({
    date: new Date().toISOString(),
    text: text.value.trim(),
    severity: sev ? parseInt(sev.value) || 3 : 3
  });
  text.value = "";
  saveHealthData();
  showNotif("📋 Síntoma registrado","var(--cy)");
}

function deleteSymptom(index){
  healthData.symptoms.splice(index,1);
  saveHealthData();
}

function renderHealthTracker(){
  // Render injection tracker
  var injectionContainer = document.getElementById("injection-tracker");
  if(injectionContainer){
    var inj = healthData.injections;
    var lastInj = inj.length > 0 ? new Date(inj[inj.length-1].date) : null;
    var now = new Date();
    
    // Calculate streak (consecutive days with at least one injection)
    var streak = 0;
    if(lastInj){
      var checkDate = new Date(now);
      checkDate.setHours(0,0,0,0);
      for(var d=0;d<365;d++){
        var found = false;
        for(var i=0;i<inj.length;i++){
          var injDate = new Date(inj[i].date);
          injDate.setHours(0,0,0,0);
          if(injDate.getTime() === checkDate.getTime()){
            found = true;
            break;
          }
        }
        if(found){
          streak++;
          checkDate.setDate(checkDate.getDate()-1);
        } else break;
      }
    }
    
    var hoursSince = lastInj ? Math.floor((now-lastInj)/3600000) : "—";
    var lastStr = lastInj ? lastInj.toLocaleString("es-ES",{hour:"2-digit",minute:"2-digit",day:"numeric",month:"short"}) : "Nunca";
    
    injectionContainer.innerHTML =
      '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">'+
      '<div style="display:flex;gap:20px;flex-wrap:wrap">'+
      '<div style="text-align:center"><div style="font-size:22px;font-weight:700;color:var(--grn)">'+streak+'</div><div style="font-size:8px;color:var(--dim);text-transform:uppercase;letter-spacing:1px">Días Seguidos</div></div>'+
      '<div style="text-align:center"><div style="font-size:22px;font-weight:700;color:var(--cy)">'+hoursSince+'</div><div style="font-size:8px;color:var(--dim);text-transform:uppercase;letter-spacing:1px">Horas Últ. Iny.</div></div>'+
      '<div style="text-align:center"><div style="font-size:14px;font-weight:600;color:var(--text)">'+lastStr+'</div><div style="font-size:8px;color:var(--dim);text-transform:uppercase;letter-spacing:1px">Última Inyección</div></div>'+
      '<div style="text-align:center"><div style="font-size:22px;font-weight:700;color:var(--go)">'+inj.length+'</div><div style="font-size:8px;color:var(--dim);text-transform:uppercase;letter-spacing:1px">Total Inyecciones</div></div>'+
      '</div>'+
      '<div style="display:flex;gap:6px">'+
      '<button class="bt bt-gr" style="padding:6px 16px;font-size:10px" onclick="markInjection()">💉 Marcar Inyección</button>'+
      '<button class="bt" style="padding:6px 10px;font-size:9px;border-color:var(--rd);color:var(--rd)" onclick="clearInjections()">🗑️</button>'+
      '</div>'+
      '</div>'+
      '<div style="margin-top:8px;padding:6px 10px;font-size:9px;color:var(--dim);border:1px solid var(--border);background:rgba(45,138,78,0.03)">'+
      '💡 Recuerda: Inyección diaria para la columna. '+(streak>0?'✅ Llevas '+streak+' día(s) consecutivo(s). ¡Sigue así!':'⚠️ Marca la primera inyección de hoy.')+
      '</div>';
  }
  
  // Render symptom history
  var symptomContainer = document.getElementById("symptom-history");
  if(symptomContainer){
    var symps = healthData.symptoms;
    if(symps.length===0){
      symptomContainer.innerHTML = '<div style="padding:12px;text-align:center;color:var(--dim);font-size:10px">No hay síntomas registrados. Agrega uno arriba.</div>';
    } else {
      var html = '';
      // Show last 10 symptoms
      var showing = symps.slice().reverse();
      if(showing.length>10) showing = showing.slice(0,10);
      for(var i=0;i<showing.length;i++){
        var s = showing[i];
        var d = new Date(s.date);
        var severityLabel = s.severity <= 2 ? 'Leve' : s.severity <= 4 ? 'Moderado' : 'Grave';
        var severityColor = s.severity <= 2 ? 'var(--grn)' : s.severity <= 4 ? 'var(--go)' : 'var(--rd)';
        var originalIndex = symps.length - 1 - i;
        html += '<div class="dr" style="padding:5px 0">'+
          '<span style="display:flex;align-items:center;gap:6px">'+
          '<span style="font-size:9px;color:'+severityColor+';font-weight:600">'+severityLabel+'</span>'+
          '<span style="font-size:10px;color:var(--text)">'+s.text+'</span>'+
          '</span>'+
          '<span style="display:flex;align-items:center;gap:8px">'+
          '<span style="font-size:8px;color:var(--dim)">'+d.toLocaleDateString("es-ES",{day:"numeric",month:"short"})+'</span>'+
          '<span onclick="deleteSymptom('+originalIndex+')" style="cursor:pointer;font-size:10px;color:var(--rd);opacity:0.5">✕</span>'+
          '</span></div>';
      }
      if(symps.length>10){
        html += '<div style="padding:4px 0;font-size:8px;color:var(--dim);text-align:center">+ '+(symps.length-10)+' síntomas anteriores</div>';
      }
      symptomContainer.innerHTML = html;
    }
  }
}

// Initialize health tracker
renderHealthTracker();

// ─── MASK/METAMASK ACCOUNT CHANGE LISTENER ───
if(window.ethereum){
window.ethereum.on("accountsChanged", function(accounts){
if(accounts.length===0){
disconnectWallet();
} else {
// Recargar datos si está conectado
var statusEl=document.getElementById("wallet-status");
if(statusEl&&statusEl.textContent!=="No conectado"&&statusEl.textContent!=="⛔ No conectado"){
connectWallet();
}
}
});
window.ethereum.on("chainChanged", function(){
if(document.getElementById("wallet-info").style.display!=="none"){
connectWallet();
}
});
}

console.log("PROYECTO INFINITO — DApp Familiar Cargada");
