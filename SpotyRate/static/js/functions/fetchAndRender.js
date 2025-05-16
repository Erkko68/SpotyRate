export async function fetchAndRender(url, container) {
  try {
    const res = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!res.ok) throw new Error(res.status);
    const html = await res.text();
    container.innerHTML = html;
  } catch (err) {
    console.error('Fetch error:', err);
    container.innerHTML = `
      <div class="p-4 text-center text-red-300">
        Something went wrong. Please try again.
      </div>`;
  }
}
