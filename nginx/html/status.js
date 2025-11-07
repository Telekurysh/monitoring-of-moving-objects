async function fetchNginxRaw(){
  try{
    const res = await fetch('/status/raw');
    const txt = await res.text();
    document.getElementById('nginx-raw').textContent = txt;
    // parse counts (simple heuristic)
    const uptimeMatch = txt.match(/Active connections:\s*(\d+)/i);
    document.getElementById('updated').textContent = new Date().toLocaleString();
    return txt;
  }catch(e){
    document.getElementById('nginx-raw').textContent = 'Ошибка: ' + e.message;
    document.getElementById('api-status').textContent = 'unknown';
    document.getElementById('db-status').textContent = 'unknown';
  }
}

async function checkApi(){
  try{
    const r = await fetch('/api/v1/');
    document.getElementById('api-status').textContent = (r.ok? 'online' : 'offline');
  }catch(e){document.getElementById('api-status').textContent = 'offline'}
}

async function checkDb(){
  try{
    const r = await fetch('/admin', { method: 'HEAD' });
    document.getElementById('db-status').textContent = (r.ok? 'online' : 'offline');
  }catch(e){document.getElementById('db-status').textContent = 'offline'}
}

async function main(){
  await fetchNginxRaw();
  await checkApi();
  await checkDb();
  // simple demo sparkline using random data
  const spark = document.getElementById('sparkline');
  let svg = '<svg width="100%" height="72" viewBox="0 0 200 72" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">';
  const pts = Array.from({length:30}, (_,i)=>Math.floor(10 + Math.random()*50));
  const step = 200/ (pts.length-1);
  svg += '<polyline fill="none" stroke="#22c55e" stroke-width="2" points="'+ pts.map((p,i)=> (i*step).toFixed(2)+','+(72-p).toFixed(2)).join(' ') +'" />';
  svg += '</svg>';
  spark.innerHTML = svg;
}

window.addEventListener('load', main);
