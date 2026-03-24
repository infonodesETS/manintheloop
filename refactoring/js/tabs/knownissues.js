'use strict';

export default async function initKnownIssues() {
  const body = document.getElementById('knownissues-body');
  try {
    const res  = await fetch('docs/data-issues.md');
    const text = await res.text();
    body.innerHTML = window.marked.parse(text);
  } catch (err) {
    body.innerHTML = `<p style="color:#ff4444">Failed to load docs/data-issues.md</p>`;
  }
}
