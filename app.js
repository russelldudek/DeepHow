if(!document.querySelector('link[href="resolver.css"]')){const resolverStyle=document.createElement('link');resolverStyle.rel='stylesheet';resolverStyle.href='resolver.css';document.head.appendChild(resolverStyle);}
const scenarios={
  knowledge:{surface:'Knowledge Capture & Transfer',platform:'Versioned work ontology',decision:'Make expertise retrievable without separating it from the work, role, equipment, and approved procedure it belongs to.',tag:'WORK://EXPERT-CAPTURE/ROLE-04/V2',state:'Knowledge addressed',identity:'Expert role · asset · SOP V2',expected:'Approved guidance sequence',observed:'Captured demonstration + narration',evidence:'Version · author · review · context',learning:'Retrieval use + SOP change'},
  output:{surface:'Operational Output Verification',platform:'Output evidence contract',decision:'Define the observable result, tolerance, confidence posture, exception class, and human review before automating the judgment.',tag:'WORK://OUTPUT-VERIFY/LOT-118/V1',state:'Output evidence set',identity:'Lot 118 · station · product',expected:'Output standard + tolerance',observed:'Completion photo or video',evidence:'Confidence + exception class',learning:'Defect pattern + standard update'},
  live:{surface:'Live SOP Verification',platform:'Sequence + latency contract',decision:'Match model confidence and response time to the consequence of a missed, late, or incorrect intervention—and preserve human authority.',tag:'WORK://LIVE-SOP/STEP-07/V3',state:'Drift threshold set',identity:'Step 07 · operator · equipment',expected:'Approved action sequence',observed:'Live action + timing',evidence:'Latency + confidence + human authority',learning:'Drift event + intervention result'},
  motion:{surface:'Time & Motion AI',platform:'Cycle and activity event model',decision:'Keep activity classification tied to the same work identity so timing variation can return as a useful improvement hypothesis.',tag:'WORK://CYCLE-ANALYSIS/CELL-12/V5',state:'Flow address resolved',identity:'Cell 12 · cycle · role',expected:'Standard activity pattern',observed:'Classified motion + duration',evidence:'Event model + uncertainty',learning:'Bottleneck + improvement hypothesis'}
};
const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
let resolutionTimer;
function setScenario(key,focus=false){
  const scenario=scenarios[key]||scenarios.knowledge;
  document.querySelectorAll('.scenario-tab').forEach(button=>button.setAttribute('aria-selected',String(button.dataset.scenario===key)));
  document.querySelectorAll('.work-source').forEach(source=>{
    const active=source.dataset.source===key;
    source.setAttribute('aria-current',String(active));
    const state=source.querySelector('.source-state');
    if(state)state.textContent=active?'Signal selected':'Available';
  });
  const ids={surface:'surface-value',platform:'platform-value',decision:'decision-value',tag:'address-tag',state:'resolver-result',identity:'coordinate-identity',expected:'coordinate-expected',observed:'coordinate-observed',evidence:'coordinate-evidence',learning:'coordinate-learning'};
  Object.entries(ids).forEach(([field,id])=>{const element=document.getElementById(id);if(element)element.textContent=scenario[field]});
  const stage=document.getElementById('work-coordinate');
  const stageState=document.getElementById('stage-state');
  if(stage){
    clearTimeout(resolutionTimer);
    stage.dataset.scenario=key;
    stage.dataset.phase='idle';
    if(stageState)stageState.textContent=reducedMotion.matches?scenario.state:'Resolving work address';
    void stage.offsetWidth;
    if(reducedMotion.matches){
      stage.dataset.phase='resolved';
    }else{
      stage.dataset.phase='resolving';
      resolutionTimer=window.setTimeout(()=>{
        stage.dataset.phase='resolved';
        if(stageState)stageState.textContent=scenario.state;
      },3000);
    }
  }
  if(focus)document.getElementById('surface-value')?.focus();
}
document.addEventListener('DOMContentLoaded',()=>{
  const proofImage=document.querySelector('.proof-photo img');
  const removeBrokenProof=()=>{if(proofImage?.complete&&proofImage.naturalWidth===0){const figure=proofImage.closest('.proof-photo');figure?.parentElement?.classList.add('single-column');figure?.remove();}};
  proofImage?.addEventListener('error',removeBrokenProof,{once:true});
  removeBrokenProof();
  const toggle=document.querySelector('.mobile-toggle'),links=document.getElementById('site-links');
  toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));links?.classList.toggle('open',!open)});
  document.querySelectorAll('.scenario-tab').forEach((button,index,buttons)=>{
    button.addEventListener('click',()=>setScenario(button.dataset.scenario));
    button.addEventListener('keydown',event=>{
      if(!['ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;
      event.preventDefault();
      let next=index;
      if(event.key==='ArrowRight')next=(index+1)%buttons.length;
      if(event.key==='ArrowLeft')next=(index-1+buttons.length)%buttons.length;
      if(event.key==='Home')next=0;
      if(event.key==='End')next=buttons.length-1;
      buttons[next].focus();
      setScenario(buttons[next].dataset.scenario);
    });
  });
  document.getElementById('reset-scenario')?.addEventListener('click',()=>setScenario('knowledge'));
  reducedMotion.addEventListener?.('change',()=>setScenario(document.getElementById('work-coordinate')?.dataset.scenario||'knowledge'));
  setScenario('knowledge');
});
