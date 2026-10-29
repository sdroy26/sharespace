// Optional progressive enhancement. All booking validation is repeated server-side.
document.addEventListener('DOMContentLoaded',()=>{const start=document.querySelector('input[name="start"]');const end=document.querySelector('input[name="end"]');if(start&&end){start.addEventListener('change',()=>{if(start.value)end.min=start.value;});}});
