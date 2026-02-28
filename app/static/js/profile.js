
document.addEventListener('DOMContentLoaded', () => {
  const modals = Array.from(document.querySelectorAll('.modal'));
  if (modals.length === 0) return;
  let showIndex = 0;
  function show(i) {
    modals.forEach((m, idx) => m.style.display = idx === i ? 'block' : 'none');
  }
  modals.forEach((modal, i) => {
    const closes = modal.querySelectorAll('.close');
    closes.forEach(el => el.addEventListener('click', () => {
      modal.style.display = 'none';
      if (i + 1 < modals.length) show(i + 1);
    }));
    window.addEventListener('click', e => {
      if (e.target === modal) {
        modal.style.display = 'none';
        if (i + 1 < modals.length) show(i + 1);
      }
    });
  });
  show(showIndex);
});