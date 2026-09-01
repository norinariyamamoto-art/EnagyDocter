(() => {
  const cfg = window.ENERGY_DOCTOR_CONFIG || {};
  const status = cfg.receptionStatus || "closed";
  const banner = document.getElementById("reception-banner");
  const formLinks = document.querySelectorAll("[data-form]");
  const setClosed = (a) => {
    a.href = "#contact";
    a.setAttribute("aria-disabled","true");
    a.classList.add("opacity-70","cursor-not-allowed");
    a.addEventListener("click", e => {
      e.preventDefault();
      document.getElementById("reception-banner")?.scrollIntoView({behavior:"smooth",block:"center"});
    });
  };
  formLinks.forEach(a => {
    if(status === "open" && cfg.publicFormUrl){ a.href=cfg.publicFormUrl; a.target="_blank"; a.rel="noopener"; }
    else if(status === "test" && cfg.testFormUrl){ a.href=cfg.testFormUrl; a.target="_blank"; a.rel="noopener"; a.textContent="社内テスト診断を開始する"; }
    else setClosed(a);
  });
  if(banner && status === "open") banner.classList.add("hidden");
  if(banner && status === "test") banner.innerHTML="<b>社内テスト受付中です。</b> 一般受付はまだ開始していません。";

  document.querySelectorAll("[data-solution]").forEach(a => {
    const u = cfg.solutionUrls?.[a.dataset.solution];
    a.href = u || "#solutions";
    if(u){a.target="_blank";a.rel="noopener";}
  });
  const b=document.getElementById("mb"),m=document.getElementById("mm");
  b?.addEventListener("click",()=>m.classList.toggle("hidden"));
  document.getElementById("yr").textContent=new Date().getFullYear();

  const modal=document.getElementById("report-modal");
  document.getElementById("open-report")?.addEventListener("click",()=>modal.classList.remove("hidden"));
  document.getElementById("close-report")?.addEventListener("click",()=>modal.classList.add("hidden"));
  modal?.addEventListener("click",e=>{if(e.target===modal) modal.classList.add("hidden")});
  document.addEventListener("keydown",e=>{if(e.key==="Escape") modal?.classList.add("hidden")});
})();