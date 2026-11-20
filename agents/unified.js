/* One storefront, two MCP endpoints. Only copy buttons; no demo or sensitive-data processing. */
(() => {
  'use strict';
  document.querySelectorAll('.unified-copy[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const original=button.textContent;
      try {
        await navigator.clipboard.writeText(button.dataset.copy);
        button.textContent='Copied';
      } catch (err) {
        button.textContent='Select the endpoint above to copy';
      }
      setTimeout(() => { button.textContent=original; }, 2200);
    });
  });
})();
