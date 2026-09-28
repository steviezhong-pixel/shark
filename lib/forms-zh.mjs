// Chinese partner forms (supplier + local services + sponsorship).
import { esc } from "./layout.mjs";

const zhFormScript = `
async function submitForm(f){
  const msg=f.querySelector('.formmsg');
  const btn=f.querySelector('button[type=submit]');
  const show=(cls,txt)=>{msg.className='formmsg '+cls;msg.textContent=txt;msg.scrollIntoView({behavior:'smooth',block:'nearest'});};
  msg.className='formmsg';msg.textContent='';
  btn.disabled=true;
  try{
    const r=await fetch(f.action,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},body:new URLSearchParams(new FormData(f))});
    const j=await r.json().catch(()=>({}));
    if(r.ok&&j.ok){f.reset();show('ok',j.message||'提交成功，我们已收到您的资料。一般一个工作日内联系您。');}
    else{show('err',(j&&j.error)||('提交失败（HTTP '+r.status+'）。请稍后重试或直接联系我们的邮箱。'));}
  }catch(e){
    show('err','网络错误——本次提交未送达，请重新提交。');
  }finally{btn.disabled=false;}
}
document.querySelectorAll('form[data-ajax]').forEach(f=>{f.addEventListener('submit',e=>{e.preventDefault();submitForm(f);});});
`;

const zhFields = (extra = "") => `
<div class="field"><label for="z-comp">公司名称 <span class="req">*</span></label>
  <input id="z-comp" name="company" required></div>
<div class="field"><label for="z-name">联系人 <span class="req">*</span></label>
  <input id="z-name" name="name" required></div>
<div class="field"><label for="z-phone">手机/微信 <span class="req">*</span></label>
  <input id="z-phone" name="contact" required placeholder="手机号或微信号"></div>
<div class="field"><label for="z-email">邮箱</label>
  <input id="z-email" name="email" type="email"></div>
${extra}`;

/** 产品供应商合作申请 */
export function supplierFormZh() {
  return `
<section class="card" id="apply">
<h2>产品供应商合作申请</h2>
<p>goChina Events 面向海外参展商与采购商提供商务接待、翻译、工厂/展厅访问与采购协调服务，为国内工厂与出口企业带来<strong>有明确采购需求的海外客户</strong>。欢迎提前填写申请；合作细节（客户归属、计佣范围、结算方式等）后续<strong>针对每个供应商单独商定，需要书面确认</strong>。</p>
<p>我们不承诺任何具体佣金比例，也不虚构客户数量；实际合作按你们的产品范围和报价决定。</p>
<form class="req" action="/api/partner/supplier" method="post" novalidate>
  ${zhFields(`
  <fieldset>
    <legend>产品与合作</legend>
    <div class="field"><label for="z-cat">主营产品 / 品类 <span class="req">*</span></label>
      <input id="z-cat" name="category" required placeholder="举例：现代风格休闲椅，主要出口欧美"></div>
    <div class="field"><label for="z-moq">起订量 &amp; 定制能力</label>
      <input id="z-moq" name="moq" placeholder="举例：MOQ 50起，可ODM；打样15天"></div>
    <div class="field"><label for="z-exp">主要出口市场</label>
      <input id="z-exp" name="export_markets" placeholder="如有：美国 / 德国 / 中东…没有也可写无"></div>
    <div class="field"><label for="z-host">接待能力</label>
      <input id="z-host" name="hosting" placeholder="展厅地址、可接待时间、谁来接待（老板/外贸）"></div>
    <div class="field"><label for="z-intent">合作意向说明</label>
      <textarea id="z-intent" name="message" placeholder="希望接触哪类买家？是否接受合作引荐费用？"></textarea></div>
  </fieldset>`)}
  <input type="hidden" name="form_type" value="product_supplier">
  <input type="hidden" name="lang" value="zh">
  <div class="formmsg" role="status" aria-live="polite"></div>
  <button type="submit" class="btn">提交合作申请</button>
  <p style="font-size:.8rem;color:#98a1ab">我们仅将资料用于合作沟通，不会公开发布您的联络信息。见 <a href="/privacy/">隐私说明</a>。</p>
</form>
</section>`;
}

/** 本地服务商合作申请 */
export function localServiceFormZh() {
  return `
<section class="card" id="apply">
<h2>本地服务商合作申请</h2>
<p>我们与酒店、车队、翻译、第三方验货和货代等本地服务商建立合作。请填实际服务范围与报价口径，方便匹配客户订单。</p>
<form class="req" action="/api/partner/local-service" method="post" novalidate>
  ${zhFields(`
  <fieldset>
    <legend>服务与覆盖</legend>
    <div class="field"><label for="z-svc">服务类型 <span class="req">*</span></label>
      <select id="z-svc" name="service_type" required>
        <option value="">请选择</option>
        <option>车辆租赁/商务用车</option>
        <option>酒店合作</option>
        <option>商务翻译</option>
        <option>验货机构</option>
        <option>货代/物流</option>
        <option>其他</option>
      </select></div>
    <div class="field"><label for="z-cities">覆盖城市 <span class="req">*</span></label>
      <input id="z-cities" name="cities" required placeholder="如：广州+佛山+深圳"></div>
    <div class="field"><label for="z-price">服务范围与报价说明</label>
      <textarea id="z-price" name="message" placeholder="车型/房型/语种/服务内容/计价方式/取消规则等"></textarea></div>
  </fieldset>`)}
  <input type="hidden" name="form_type" value="local_service">
  <input type="hidden" name="lang" value="zh">
  <div class="formmsg" role="status" aria-live="polite"></div>
  <button type="submit" class="btn">提交合作申请</button>
</form>
</section>`;
}

/** 中方赞助/参会合作 Inquiry form (buyer-meetups/sponsorship) */
export function sponsorshipFormZh() {
  return `
<section class="card" id="sponsor">
<h2>买家小会赞助 / 参会合作意向</h2>
<div class="notice"><p><strong>请先注意：</strong>目前尚未确认任何具体小会的日期、场地和已到场 ．买家名单。本页只收集合作意向和需求，用于<strong>确认真实组办条件后再正式报价和收款</strong>。我们不提前发售未保障的活动票，也不承诺买家到场。</p></div>
<form class="req" action="/api/partner/sponsorship" method="post" novalidate>
  ${zhFields(`
  <fieldset>
    <legend>您的业务与需求</legend>
    <div class="field"><label for="z-ind">您的行业 / 产品 <span class="req">*</span></label>
      <input id="z-ind" name="industry" required placeholder="如：宠物用品供应链 / 酒店家具"></div>
    <div class="field"><label for="z-goal">希望接触的海外买家类型</label>
      <input id="z-goal" name="target_buyers" placeholder="市场、品类、业务模式（如：美国电商卖场 / 中东酒店采购）"></div>
    <div class="field"><label for="z-show">关注哪场展会？</label>
      <input id="z-show" name="show" placeholder="如：广交会 / CIFS宠展 / HOTELEX…也可留空"></div>
    <div class="field"><label for="z-note">想了解的合作内容</label>
      <textarea id="z-note" name="message" placeholder="席位/对接/赞助：您希望获得什么权益或合作形式？"></textarea></div>
  </fieldset>
  <div class="field"><label style="font-weight:normal"><input type="checkbox" name="consent" value="yes" required> 我知道活动未确认，仅提交合作意向 <span class="req">*</span></label></div>`)}
  <input type="hidden" name="form_type" value="sponsorship">
  <input type="hidden" name="lang" value="zh">
  <div class="formmsg" role="status" aria-live="polite"></div>
  <button type="submit" class="btn">提交意向</button>
</form>
</section>`;
}

export { zhFormScript };
