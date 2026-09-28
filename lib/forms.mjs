import { esc } from "./layout.mjs";

/** Shared client-side submit handler. Shows success ONLY after server 200. */
export const formScript = `
async function submitForm(f){
  const msg=f.querySelector('.formmsg');
  const btn=f.querySelector('button[type=submit]');
  const show=(cls,txt)=>{msg.className='formmsg '+cls;msg.textContent=txt;msg.scrollIntoView({behavior:'smooth',block:'nearest'});};
  msg.className='formmsg';msg.textContent='';
  btn.disabled=true;btn.setAttribute('aria-busy','true');
  try{
    const r=await fetch(f.action,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},body:new URLSearchParams(new FormData(f))});
    const j=await r.json().catch(()=>({}));
    if(r.ok&&j.ok){f.reset();show('ok',j.message||'Thank you. Your inquiry has been received. We reply within one business day.');}
    else{show('err',(j&&j.error)||('Submission failed (HTTP '+r.status+'). Please retry or use our contact page.'));}
  }catch(e){
    show('err','Network error — your inquiry was NOT sent. Please retry.');
  }finally{btn.disabled=false;btn.removeAttribute('aria-busy');}
}
document.querySelectorAll('form[data-ajax]').forEach(f=>{f.addEventListener('submit',e=>{e.preventDefault();submitForm(f);});});
`;

/* Collect referrer & UTM params as hidden inputs */
export const utmFields = () => {
  const p = new URLSearchParams(typeof location !== "undefined" ? location.search : "");
  const fields = { utm_source: "", utm_medium: "", utm_campaign: "", ref_page: typeof document !== "undefined" && document.referrer || "" };
  ["utm_source", "utm_medium", "utm_campaign"].forEach((k) => { if (p.get(k)) fields[k] = p.get(k); });
  return Object.entries(fields).map(([k, v]) => `<input type="hidden" name="${k}" value="${esc(v)}">`).join("");
};

/** English buyer inquiry form v2 — step 1 core fields; step 2 in a <details> block. */
export function buyerForm({ SITE, ctx = {}, compact = false, heading = "Plan My Trip" } = {}) {
  return `
<section class="card" id="inquiry">
  <h2>${esc(heading)}</h2>
  ${compact ? "" : `<p>Tell us the essentials; we reply within one business day. Nothing needs to be fully decided yet.</p>`}
  <form class="req" action="/api/lead" method="post" novalidate>
    <div class="field"><label for="f-name">Name <span class="req">*</span></label>
      <input id="f-name" name="name" required autocomplete="name"></div>
    <div class="field"><label for="f-contact">Email or WhatsApp <span class="req">*</span></label>
      <input id="f-contact" name="contact" type="text" required placeholder="you@company.com or +86 … / +1 …"></div>
    <div class="field"><label for="f-when">Planned visit to China <span class="req">*</span></label>
      <input id="f-when" name="dates" required placeholder="e.g. late November, not fixed"></div>
    <div class="field"><label for="f-need">Industry / products & what you need <span class="req">*</span></label>
      <textarea id="f-need" name="message" required placeholder="e.g. hotel furniture + lighting supplier visits around my Canton Fair trip"></textarea></div>
    <details class="optional"><summary>More trip context (optional — helps us quote precisely)</summary>
      <fieldset>
        <legend>Optional details</legend>
        <div class="field"><label for="f-service">Main service</label>
          <select id="f-service" name="service">
            <option value="">Not decided yet</option>
            ${["Trade show attendance support", "Airport transfer", "Business vehicle & driver", "Hotel arrangements", "Business interpreter", "Supplier research & shortlisting", "Showroom & factory visits", "Full sourcing trip", "Post-trip purchasing coordination", "Inspection & shipping coordination"].map((o) => `<option>${o}</option>`).join("")}
          </select></div>
        <div class="field"><label for="f-city">City or trade show</label>
          <input id="f-city" name="city_show" value="${esc(ctx.show || ctx.industry || "")}" placeholder="e.g. Canton Fair, Guangzhou/Foshan"></div>
        <div class="field"><label for="f-qty">Approx. quantity / order size</label>
          <input id="f-qty" name="quantity" placeholder="e.g. 1 x 40ft container"></div>
        <div class="field"><label for="f-budget">Budget range</label>
          <input id="f-budget" name="budget" placeholder="A rough range is fine"></div>
        <div class="field"><label for="f-role">Your role</label>
          <input id="f-role" name="role" placeholder="Owner / buyer / agent..."></div>
      </fieldset>
    </details>
    <input type="hidden" name="source_page" value="${esc(ctx.source || "/plan-your-trip/")}">
    <input type="hidden" name="lang" value="en">
    <input type="hidden" name="company_website" value=""><!-- honeypot -->
    ${utmFields()}
    <div class="formmsg" role="status" aria-live="polite"></div>
    <button type="submit" class="btn">Send inquiry</button>
    <p class="hint" style="font-size:.8rem;color:#98a1ab">Used only for replying and trip planning — <a href="/privacy/">privacy</a>.</p>
  </form>
</section>`;
}

/** Buyer Meetups — independent interest form (EN). */
export function meetupsForm({eep} = {}) {
  return `
<section class="card" id="meetups-form">
  <h2>Buyer meetups — interest list</h2>
  <p>No events are confirmed yet — this form only records your interest matching so invitations reach the right people when an event becomes real.</p>
  <form class="req" action="/api/meetup" method="post" novalidate>
    <div class="field"><label for="m-name">Name <span class="req">*</span></label>
      <input id="m-name" name="name" required></div>
    <div class="field"><label for="m-contact">Email or WhatsApp <span class="req">*</span></label>
      <input id="m-contact" name="contact" type="text" required></div>
    <div class="field"><label for="m-role">You are a <span class="req">*</span></label>
      <select id="m-role" name="attendee_type" required>
        <option value="">Select…</option>
        <option>Buyer / importer</option>
        <option>E-commerce seller</option>
        <option>Supplier / factory representative</option>
        <option>Agent / intermediary</option>
      </select></div>
    <div class="field"><label for="m-country">Your country / market <span class="req">*</span></label>
      <input id="m-country" name="country" required></div>
    <div class="field"><label for="m-show">Trade show you plan to attend</label>
      <input id="m-show" name="show" placeholder="e.g. Canton Fair / CIPS / HOTELEX — or none"></div>
    <div class="field"><label for="m-cat">Product categories you buy or sell</label>
      <input id="m-cat" name="categories"></div>
    <div class="field"><label for="m-date">Expected dates in China</label>
      <input id="m-date" name="dates"></div>
    <div class="field"><label style="font-weight:normal"><input type="checkbox" name="open_refs" value="yes"> OK to receive matched supplier introductions</label></div>
    <input type="hidden" name="lang" value="en">
    <input type="hidden" name="company_website" value=""><!-- honeypot -->
    <div class="formmsg" role="status" aria-live="polite"></div>
    <button type="submit" class="btn">Add me to the interest list</button>
  </form>
</section>`;
}
